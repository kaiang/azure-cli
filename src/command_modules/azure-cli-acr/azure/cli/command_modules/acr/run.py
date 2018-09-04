# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.log import get_logger
from knack.util import CLIError

import os
import uuid
import tempfile

from ._run_polling import get_run_with_polling

from .sdk.models import (
    FileTaskRunRequest,
    PlatformProperties,
    OS,
    EncodedTaskRunRequest
)
from azure.cli.core.commands import LongRunningOperation

from ._stream_utils import stream_logs
from ._utils import validate_managed_registry
from ._client_factory import cf_acr_registries_build
from ._archive_utils import upload_source_code, check_remote_source_code

RUN_NOT_SUPPORTED = 'Run is only available for managed registries.'

logger = get_logger(__name__)


def acr_run(cmd,
            client,
            registry_name,
            source_location,
            task_file='acb.yaml',
            values_file=None,
            encoded_task=None,
            encoded_values=None,
            set_value=None,
            no_format=False,
            no_logs=False,
            timeout=None,
            resource_group_name=None,
            os_type=OS.linux):

    _, resource_group_name = validate_managed_registry(
        cmd.cli_ctx, registry_name, resource_group_name, RUN_NOT_SUPPORTED)

    # TODO: Remove this import once the SDK is merged.
    from ._client_factory import cf_acr_registries_build
    client_registries = cf_acr_registries_build(cmd.cli_ctx)

    if os.path.exists(source_location):
        if not os.path.isdir(source_location):
            raise CLIError(
                "Source location should be a local directory path or remote URL.")

        tar_file_path = os.path.join(tempfile.gettempdir(
        ), 'run_archive_{}.tar.gz'.format(uuid.uuid4().hex))

        try:
            source_location = upload_source_code(
                client_registries, registry_name, resource_group_name,
                source_location, tar_file_path, "", "")
        except Exception as err:
            raise CLIError(err)
        finally:
            try:
                logger.debug(
                    "Deleting the archived source code from '%s'...", tar_file_path)
                os.remove(tar_file_path)
            except OSError:
                pass
    else:
        source_location = check_remote_source_code(source_location)
        logger.warning(
            "Sending context to {}.azurecr.io...".format(registry_name))

    if encoded_task:
        request = EncodedTaskRunRequest(
            encoded_task_content=encoded_task,
            encoded_values_content=encoded_values,
            values=(set_value if set_value else []),
            timeout=timeout,
            platform=PlatformProperties(os=os_type)
        )
    else:
        request = FileTaskRunRequest(
            task_file_path=task_file,
            values_file_path=values_file,
            values=(set_value if set_value else []),
            source_location=source_location,
            timeout=timeout,
            platform=PlatformProperties(os=os_type)
        )

    queued = LongRunningOperation(cmd.cli_ctx)(client_registries.schedule_run(
        resource_group_name=resource_group_name,
        registry_name=registry_name,
        run_request=request))

    id = queued.run_id
    logger.warning("Queued a run with ID: %s", id)
    logger.warning("Waiting for agent...")

    if no_logs:
        return get_run_with_polling(client, id, registry_name, resource_group_name)

    return stream_logs(client, id, registry_name, resource_group_name, no_format, True)
