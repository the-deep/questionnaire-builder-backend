import typing
import strawberry
from strawberry.utils.str_converters import to_camel_case


ResultTypeVar = typing.TypeVar("ResultTypeVar")


ARRAY_NON_MEMBER_ERRORS = 'nonMemberErrors'

# generalize all the CustomErrorType
CustomErrorType = strawberry.scalar(
    typing.NewType("CustomErrorType", object),
    description="A generic type to return error messages",
    serialize=lambda v: v,
    parse_value=lambda v: v,
)


@strawberry.type
class ArrayNestedErrorType:
    key: str
    messages: typing.Optional[str]
    objectErrors: typing.Optional[list[typing.Optional[CustomErrorType]]]

    def keys(self):
        return ['key', 'messages', 'objectErrors']

    def __getitem__(self, key):
        key = key
        if key in ('objectErrors',) and getattr(self, key):
            return [dict(each) for each in getattr(self, key)]
        return getattr(self, key)


@strawberry.type
class _CustomErrorType:
    field: str
    messages: typing.Optional[str]
    objectErrors: typing.Optional[
        list[typing.Optional[CustomErrorType]]
    ]
    arrayErrors: typing.Optional[
        list[typing.Optional[ArrayNestedErrorType]]
    ]

    def keys(self):
        return ['field', 'messages', 'objectErrors', 'arrayErrors']

    def __getitem__(self, key):
        key = key
        if key in ('objectErrors', 'arrayErrors') and getattr(self, key):
            return [dict(each) for each in getattr(self, key)]
        return getattr(self, key)


def serializer_error_to_error_types(errors: dict, initial_data: dict | None = None) -> list:
    initial_data = initial_data or dict()
    error_types = list()
    for field, value in errors.items():
        if isinstance(value, dict):
            error_types.append(_CustomErrorType(
                field=to_camel_case(field),
                objectErrors=value,
                arrayErrors=None,
                messages=None,
            ))
        elif isinstance(value, list):
            if isinstance(value[0], str):
                if isinstance(initial_data.get(field), list):
                    # we have found an array input with top level error
                    error_types.append(_CustomErrorType(
                        field=to_camel_case(field),
                        arrayErrors=[ArrayNestedErrorType(
                            key=ARRAY_NON_MEMBER_ERRORS,
                            messages=''.join(str(msg) for msg in value),
                            objectErrors=None,
                        )],
                        messages=None,
                        objectErrors=None,
                    ))
                else:
                    error_types.append(_CustomErrorType(
                        field=to_camel_case(field),
                        messages=''.join(str(msg) for msg in value),
                        objectErrors=None,
                        arrayErrors=None,
                    ))
            elif isinstance(value[0], dict):
                arrayErrors = []
                for pos, array_item in enumerate(value):
                    if not array_item:
                        # array item might not have error
                        continue
                    # fetch array.item.uuid from the initial data
                    key = initial_data[field][pos].get('uuid', f'NOT_FOUND_{pos}')
                    arrayErrors.append(ArrayNestedErrorType(
                        key=key,
                        objectErrors=serializer_error_to_error_types(array_item, initial_data[field][pos]),
                        messages=None,
                    ))
                error_types.append(_CustomErrorType(
                    field=to_camel_case(field),
                    arrayErrors=arrayErrors,
                    objectErrors=None,
                    messages=None,
                ))
        else:
            # fallback
            error_types.append(_CustomErrorType(
                field=to_camel_case(field),
                messages=' '.join(str(msg) for msg in value),
                arrayErrors=None,
                objectErrors=None,
            ))
    return error_types


def mutation_is_not_valid(serializer) -> CustomErrorType | None:
    """
    Checks if serializer is valid, if not returns list of errorTypes
    """
    if not serializer.is_valid():
        errors = serializer_error_to_error_types(serializer.errors, serializer.initial_data)
        return CustomErrorType([dict(each) for each in errors])
    return None


@strawberry.type
class MutationResponseType(typing.Generic[ResultTypeVar]):
    ok: bool = True
    errors: typing.Optional[CustomErrorType] = None
    result: typing.Optional[ResultTypeVar] = None


@strawberry.type
class MutationEmptyResponseType():
    ok: bool = True
    errors: typing.Optional[CustomErrorType] = None
