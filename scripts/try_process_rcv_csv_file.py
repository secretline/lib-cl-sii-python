#!/usr/bin/env python
"""
TODO
==============

Does X and Y, and then Z.

Example
-------

TOD
For example, to do X, run::

    ./scripts/example.py arg1 arg2 arg3

"""
import logging
import os
import sys
from datetime import datetime

try:
    import cl_sii  # noqa: F401
except ImportError:
    # If package 'cl-sii' is not installed, try appending the project repo directory to the
    #   Python path, assuming thath we are in the project repo. If not, it will fail nonetheless.
    sys.path.append(os.path.dirname(os.path.abspath(__name__)))
    import cl_sii  # noqa: F401

import cl_sii.rcv.parse
from cl_sii.libs import file_processing
from cl_sii.rut import Rut


logger = logging.getLogger(__name__)
root_logger = logging.getLogger()


###############################################################################
# logging config
###############################################################################

_loggers = [logger, logging.getLogger('cl_sii')]
for _logger in _loggers:
    _logger.addHandler(logging.StreamHandler())
    _logger.setLevel(logging.INFO)

root_logger.setLevel(logging.WARNING)


###############################################################################
# script
###############################################################################

def main(
    rcv_owner_rut: Rut,
    rcv_owner_razon_social: str,
    input_file_path: str,
    output_file_path: str,
    n_rows_offset: int = 0,
    max_data_rows: int = 10000,
) -> None:
    start_ts = datetime.now()

    try:
        n_rows_proccesed, row_errors = cl_sii.rcv.parse.process_rcv_csv_file(
            rcv_owner_rut,
            rcv_owner_razon_social,
            input_file_path,
            output_file_path,
            n_rows_offset,
            max_data_rows)

        if n_rows_proccesed == 0:
            logger.warning("No rows were processed.")
        else:
            logger.info(f"Rows processed: {n_rows_proccesed}")
        if row_errors:
            logger.error("Errors processing rows:\n%s", repr(row_errors))
    except FileNotFoundError:
        logger.exception(
            "Process aborted: a file could not be opened.")
    except file_processing.MaxRowsExceeded:
        logger.warning(
            "Process stopped: the max number of data rows limit was reached.", exc_info=True)
    except KeyboardInterrupt:
        logger.error("Process interrupted by user.")
    except Exception:
        logger.exception("Process aborted.")
    finally:
        try:
            print("Action: clean up resources and connections")
            logger.info("Cleaned up resources and connections.")
        except Exception:
            logger.exception("Failed to clean up resources and connections.")

        finish_ts = datetime.now()
        duration = finish_ts - start_ts

        logger.info(f"start: {start_ts.isoformat()}")
        logger.info(f"finish: {finish_ts.isoformat()}")
        logger.info(f"duration: {duration!s}")


if __name__ == '__main__':
    # main(
    #     rcv_owner_rut=Rut(sys.argv[1], validate_dv=True),
    #     rcv_owner_razon_social=sys.argv[2],
    #     input_file_path=sys.argv[3],
    #     output_file_path=sys.argv[4],
    #     n_rows_offset=int(sys.argv[5]),
    #     max_data_rows=int(sys.argv[6]),
    # )
    main(
        rcv_owner_rut=Rut('76389992-6', validate_dv=True),
        rcv_owner_razon_social='ST CAPITAL S.A.',
        input_file_path='wip/rcv/RCV_COMPRA_REGISTRO_76389992-6_201904.csv',
        output_file_path='wip/rcv/RCV_COMPRA_REGISTRO_76389992-6_201904 output.csv',
        n_rows_offset=0,
        # max_data_rows=int(sys.argv[5]),
    )
