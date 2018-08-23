# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is
# regenerated.
# --------------------------------------------------------------------------

from .task_step_properties import TaskStepProperties


class RunTaskStep(TaskStepProperties):
    """The properties of a generic task run step.

    :param type: Constant filled by server.
    :type type: str
    :param task_definition_content: Base64 encoded value of the
     template/definition file content.
    :type task_definition_content: str
    :param values_content: Base64 encoded value of the parameters/values file
     content.
    :type values_content: str
    """

    _validation = {
        'type': {'required': True},
        'task_definition_content': {'required': True},
    }

    _attribute_map = {
        'type': {'key': 'type', 'type': 'str'},
        'task_definition_content': {'key': 'taskDefinitionContent', 'type': 'str'},
        'values_content': {'key': 'valuesContent', 'type': 'str'},
    }

    def __init__(self, task_definition_content, values_content=None):
        super(RunTaskStep, self).__init__()
        self.task_definition_content = task_definition_content
        self.values_content = values_content
        self.type = 'RunTask'
