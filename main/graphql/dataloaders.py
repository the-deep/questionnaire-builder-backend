from django.utils.functional import cached_property

from apps.questionnaire.dataloaders import QuestionnaireDataLoader


class GlobalDataLoader:

    @cached_property
    def questionnaire(self):
        return QuestionnaireDataLoader()
