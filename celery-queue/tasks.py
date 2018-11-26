import os
from collections import namedtuple
from time import sleep
from typing import List
import types

from google.oauth2 import service_account
from googleapiclient.discovery import build
from uritemplate import URITemplate

from celery import Celery, states
from celery.exceptions import Ignore
from celery.schedules import crontab
from celery.signals import celeryd_after_setup
from celery.utils.log import get_task_logger
from typing_extensions import Final

logger = get_task_logger(__name__)

SHEETS_APPEND_URL: Final = URITemplate(
    "https://sheets.googleapis.com/v4/spreadsheets{/spreadsheetId}/values{/range_}:append"
)
SHEETS_GET_URL: Final = URITemplate(
    "https://sheets.googleapis.com/v4/spreadsheets{/spreadsheetId}/values{/range_}"
)
SHEETS_UPDATE_URL: Final = URITemplate(
    "https://sheets.googleapis.com/v4/spreadsheets{/spreadsheetId}/values{/range_}"
)

SHEETS_SCOPE: Final = "https://www.googleapis.com/auth/spreadsheets"
EMAIL_SCOPE: Final = "https://www.googleapis.com/auth/userinfo.profile"
PROFILE_SCOPE: Final = "https://www.googleapis.com/auth/userinfo.email"


def config_from_pyfile(file_name):
    """Same as flask's from_pyfile but for Celery.

    From
    https://stackoverflow.com/questions/46710214/how-to-use-config-from-envvar-in-celery

    """
    d = types.ModuleType("config")
    d.__file__ = file_name
    with open(file_name, mode="rb") as fp:
        exec(compile(fp.read(), file_name, "exec"), d.__dict__)
    return d


def make_celery(name):
    """Create context tasks in Celery."""
    cfg = config_from_pyfile(os.getenv("CUB_SIGN_IN_CONFIG"))
    celery = Celery(name, broker=cfg.CELERY_BROKER_URL)
    celery.config_from_object(cfg)

    class ContextTask(celery.Task):
        abstract = True

        def __call__(self, *args, **kwargs):
            return self.run(self, *args, **kwargs)

    celery.Task = ContextTask

    @celeryd_after_setup.connect
    def setup_name_autocomplete(sender, instance, **kwargs):
        # Run the tasks now so we have some autocomplete
        update_name_autocomplete.delay(
            instance.app.conf["NAMES_FILE"],
            instance.app.conf["SPREADSHEET_ID"],
            [instance.app.conf["ROLL_SHEET"], instance.app.conf["NAMES_SHEET"]],
        )

        # Set up the autocomplete task to run every Monday at 12am.
        sender.add_periodic_task(
            crontab(hour=0, minute=0, day_of_week=1),
            update_name_autocomplete.s(
                instance.app.conf["NAMES_FILE"],
                instance.app.conf["SPREADSHEET_ID"],
                [instance.app.conf["ROLL_SHEET", instance.app.conf["NAMES_SHEET"]]],
            ),
        )

    return celery


celery = make_celery("tasks")


def make_sheets_client(service_creds_file):
    creds = service_account.Credentials.from_service_account_file(
        service_creds_file,
        scopes=["profile", "email", SHEETS_SCOPE],
    )
    creds.with_scopes([SHEETS_SCOPE])
    return build("sheets", "v4", credentials=creds).spreadsheets()


@celery.task(name="tasks.update_name_autocomplete")
def update_name_autocomplete(
    self, names_file: str = "", spreadsheet_id: str = "", sheet_names: List[str] = []
) -> None:
    """Update the `name_file` with the names pull from `sheet_names` in
    `spreadsheet_id`. This allows us to have autocomplate for cub names."""
    sheets = make_sheets_client(self._get_app().conf["SERVICE_ACCOUNT_CREDS"])
    names = []
    for sheet_name in sheet_names:
        result = (
            sheets.values()
            .get(spreadsheetId=spreadsheet_id, range=f"{sheet_name}!A2:A")
            .execute()
        )
        if result.get("values"):
            for name in result["values"]:
                names.append(name[0])
        else:
            logger.debug(f"No 'values' field in {result}")
    logger.debug(f"Found {len(names)} for autocomplete: {names}")

    with open(names_file, "w") as f:
        f.write("\n".join(names))


@celery.task(name="tasks.add_sign_in")
def add_sign_in(
    self,
    cub_name: str = "",
    cub_sig: str = "",
    parent_sig: str = "",
    time: str = "",
    date: str = "",
    spreadsheet_id: str = "",
    sheet_name: str = "",
) -> None:
    """Add a sign in record to the sheet. This function simple appends a
    row to the table containing the cub's name and signature, the parent's
    name and signature and a timestamp.

    """
    sheets = make_sheets_client(self._get_app().conf["SERVICE_ACCOUNT_CREDS"])
    append = append_row(
        sheets,
        spreadsheet_id,
        sheet_name,
        [cub_name, cub_sig, parent_sig, "", time, "", date],
    )
    if not append.ok:
        self.update_state(state=states.FAILURE, meta=append.message)
        raise Ignore()


@celery.task(name="tasks.add_sign_out")
def add_sign_out(
    self,
    cub_name: str = "",
    parent_sig: str = "",
    time: str = "",
    date: str = "",
    spreadsheet_id: str = "",
    sheet_name: str = "",
) -> None:
    """Record a sign out on the Google Sheet. This function is slightly
    more complex than :func:`add_sign_in` because it updates the row with
    the sign in corresponding to this sign out. To do this it looks for a
    row with the same cub_name and a timestamp for the same day. If it
    cannot find the appropriate record then it appends a new record to the
    table like :func:`add_sign_in`.

    """
    logger.debug("Received sign out task")
    sheets = make_sheets_client(self._get_app().conf["SERVICE_ACCOUNT_CREDS"])
    result = (
        sheets.values().get(spreadsheetId=spreadsheet_id, range=sheet_name).execute()
    )

    logger.debug(f"Get sheet result: {result}")

    updated_row_index = -1
    updated_row = ()
    for i, row in enumerate(result["values"]):
        (
            row_cub_name,
            row_cub_sig,
            row_parent_sign_in,
            _,
            row_time_in,
            _,
            row_date,
        ) = row
        if row_cub_name == cub_name and row_date == date:
            updated_row_index = i
            updated_row = (
                cub_name,
                row_cub_sig,
                row_parent_sign_in,
                parent_sig,
                row_time_in,
                time,
                date,
            )

    if updated_row_index == -1:
        logger.info("Unable to find corresponding sign in record, appending row")
        append = append_row(
            sheets,
            spreadsheet_id,
            sheet_name,
            [cub_name, "", "", parent_sig, "", time, date],
        )
        if not append.ok:
            self.update_state(state=states.FAILURE, meta=append.message)
            raise Ignore()
        return

    logger.info(f"Found corresponding sign in record, updating row {updated_row}")
    result = (
        sheets.values()
        .update(
            spreadsheetId=spreadsheet_id,
            valueInputOption="RAW",
            range=f"{sheet_name}!A{updated_row_index + 1}",
            body={
                "range": f"{sheet_name}!A{updated_row_index + 1}",
                "majorDimension": "ROWS",
                "values": [updated_row],
            },
        )
        .execute()
    )
    logger.debug(f"Update result: {result}")
    logger.debug(f"Updated record with sign out date: {updated_row}")


def append_row(sheets, spreadsheet_id: str, sheet_name: str, row: List[str]) -> bool:
    """Append a row to the sheet with the specified values."""
    AppendResult = namedtuple("AppendResult", ["ok", "message"])
    result = (
        sheets.values()
        .append(
            spreadsheetId=spreadsheet_id,
            range=sheet_name,
            valueInputOption="RAW",
            body={"values": [row]},
        )
        .execute()
    )
    logger.debug(f"Append result: {result}")
    return AppendResult(ok=True, message="Successfully appended row")
