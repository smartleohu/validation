import traceback
from enum import Enum

from fastapi import status


class ErrorCode(str, Enum):
    """Associates an error code with a specific HTTP code."""

    # Technical error
    TECHNICAL_ERROR = status.HTTP_500_INTERNAL_SERVER_ERROR
    # Functional Error
    FUNCTIONAL_ERROR = status.HTTP_400_BAD_REQUEST
    # Generic Error
    GENERIC_ERROR = status.HTTP_500_INTERNAL_SERVER_ERROR

    # Technical error
    INNITIALIZATION_ERROR = status.HTTP_500_INTERNAL_SERVER_ERROR
    EXECUTION_ERROR = status.HTTP_500_INTERNAL_SERVER_ERROR
    MISSING_TOKEN = status.HTTP_401_UNAUTHORIZED
    AUTHENTICATION_ERROR = status.HTTP_401_UNAUTHORIZED
    CHATGPT_RESPONSE_ERROR = status.HTTP_502_BAD_GATEWAY
    API_ERROR = status.HTTP_502_BAD_GATEWAY
    NOT_VALID = status.HTTP_401_UNAUTHORIZED
    MISSING_ENV_VARIABLE = status.HTTP_500_INTERNAL_SERVER_ERROR
    LOGGER_ERROR = status.HTTP_500_INTERNAL_SERVER_ERROR

    # Functional Error
    DATA_NOT_FOUND = status.HTTP_404_NOT_FOUND
    DATA_ALREADY_EXIST = status.HTTP_409_CONFLICT
    NO_MATCHING_ACTION = status.HTTP_404_NOT_FOUND
    FILE_GENERATION_ERROR = status.HTTP_500_INTERNAL_SERVER_ERROR
    PARSING_EXCEPTION = status.HTTP_400_BAD_REQUEST
    NO_RESPONSE = status.HTTP_400_BAD_REQUEST
    MISSING_DATA = status.HTTP_404_NOT_FOUND
    MISSING_PARAMETER = status.HTTP_400_BAD_REQUEST
    NO_TEMPLATE_FOUND = status.HTTP_500_INTERNAL_SERVER_ERROR
    FORMAT_ERROR = status.HTTP_400_BAD_REQUEST
    SEVERAL_EMPLOYEES_IDS_ERROR = status.HTTP_400_BAD_REQUEST
    NO_EMPLOYEE_ID_ERROR = status.HTTP_400_BAD_REQUEST
    NO_RESOURCE_ACCESS = status.HTTP_403_FORBIDDEN

    # Generic Error
    VALIDATION_ERROR = status.HTTP_422_UNPROCESSABLE_ENTITY
    DATABASE_ERROR = status.HTTP_500_INTERNAL_SERVER_ERROR
    UNEXPECTED_ERROR = status.HTTP_500_INTERNAL_SERVER_ERROR
    NO_ENTITY = status.HTTP_406_NOT_ACCEPTABLE
    JOB_ERROR = status.HTTP_404_NOT_FOUND
    JOB_UPDATE = status.HTTP_500_INTERNAL_SERVER_ERROR
    JOB_NOT_FINISHED = status.HTTP_500_INTERNAL_SERVER_ERROR

    # Error for hendling atachements sending via email
    FILE_NOT_FOUND = status.HTTP_404_NOT_FOUND
    FILE_SIZE_EXCEEDED = status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
    FILE_CREATION_ERROR = status.HTTP_500_INTERNAL_SERVER_ERROR


class BaseAppException(Exception):
    def __init__(
        self,
        message: str,
        error_code: ErrorCode,
        level: str,
        status_code: status = None,
        capture_traceback: bool = False,
        exact_message: bool = True,
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = (
            status_code if status_code else getattr(error_code, "value", 500)
        )
        self.traceback = traceback.format_exc() if capture_traceback else None
        self.level = level
        self.exact_message = exact_message
        super().__init__(self.message)

    def __str__(self):
        return f"[{self.level}] {self.__class__.__name__} ({self.status_code}): {self.message}"


# Technical Exception
class TechnicalException(BaseAppException):
    """Define technical exception"""

    def __init__(self, message: str, error_code: ErrorCode):
        level = __class__.__name__
        super().__init__(
            message, error_code=error_code, level=level, capture_traceback=True
        )


# Functional Exception
class FunctionalException(BaseAppException):
    """Define functional exception"""

    def __init__(self, message: str, error_code: ErrorCode, exact_message: bool = True):
        self.level = __class__.__name__
        self.exact_message = exact_message
        super().__init__(
            message,
            error_code=error_code,
            level=self.level,
            exact_message=exact_message,
        )


# Generic Exception
class GenericException(BaseAppException):
    """Define generic exception"""

    def __init__(self, message: str, status_code: int, error_code: ErrorCode):
        self.level = __class__.__name__
        super().__init__(
            message,
            error_code=error_code,
            level=self.level,
            status_code=status_code,
            capture_traceback=False,
        )


# Technical Exception
class InnizializationTableException(TechnicalException):
    """
    Exception thrown when an error occurs during table initialization.
    """

    def __init__(self):
        message = "Une erreur est survenue lors de l'innitialization des tables"
        super().__init__(message, ErrorCode.INNITIALIZATION_ERROR)


class LoggerException(TechnicalException):
    """
    Exception thrown when required logger.
    param :
        logger_level: level of the logger is not compatible.
    """

    def __init__(self, logger_level: str):
        message = f"Le logger {logger_level} level est incompatible."
        super().__init__(message, error_code=ErrorCode.LOGGER_ERROR)


class EnvironmentParameterMissing(TechnicalException):
    """
    Exception thrown when required environment variables are missing.
    param :
        var_name: Name of the missing environment variable.
    """

    def __init__(self, var_name: str):
        message = f"La variable d'environnement {', '.join(var_name)} est requise mais absente."
        super().__init__(message, error_code=ErrorCode.MISSING_ENV_VARIABLE)
        self.var_name = var_name


class ExecutionException(TechnicalException):
    """
    Exception thrown when an error occurs during the execution of a method.

    param:
        method_used: Name of the method or query that failed.
    """

    def __init__(self, method_used: str, details: str = None):
        message = f"Une erreur est survenue lors de l'exécution de la requête {method_used}.  {details}"
        super().__init__(message, ErrorCode.EXECUTION_ERROR)


class MissingToken(TechnicalException):
    """
    Exception thrown when the authentication token is missing or invalid.
    """

    def __init__(self):
        message = "Le token d'authentification est manquant ou invalide."
        super().__init__(message, ErrorCode.MISSING_TOKEN)


class AuthenticationException(TechnicalException):
    """
    Exception thrown when a resource requires authentication.
    """

    def __init__(self):
        message = "Vous devez être authentifié pour accéder à cette ressource."
        super().__init__(message, ErrorCode.AUTHENTICATION_ERROR)


class ChatGPTResponseException(TechnicalException):
    """
    Exception thrown when an error occurs in communication with ChatGPT.

    param:
        detail: Details of the error encountered during communication.
    """

    def __init__(self, detail: str = None):
        message = (
            f"Une erreur est survenue lors de la communication avec ChatGPT : {detail}"
        )
        super().__init__(message, ErrorCode.CHATGPT_RESPONSE_ERROR)


class ApiException(TechnicalException):
    """
    Exception thrown when an error occurs during interaction with an API.

    :param:
        api_path: Path to the API that returned an error.
    """

    def __init__(self, status_code: int, api_path: str = None, detail: str = None):
        message = f"L'API a retourné une erreur sur le chemin : {api_path} with status_code : {status_code}. {detail}"
        super().__init__(message, ErrorCode.API_ERROR)


class NetworkException(TechnicalException):
    """
    Exception thrown when a network error occurs.
    """

    def __init__(self, detail: str):
        message = f"Erreur réseau lors de la communication avec OpenAI : {detail}"
        super().__init__(message, error_code=ErrorCode.TECHNICAL_ERROR)


class PackageNotFound(TechnicalException):
    """
    Exception thrown when a Package not found.
    """

    def __init__(self, detail: str):
        message = f"Package n'a pas été trouvé ou installé : {detail}"
        super().__init__(message, error_code=ErrorCode.TECHNICAL_ERROR)


class DataBaseException(TechnicalException):
    """
    Exception thrown when the db query fail for an unexpected reason
    """

    def __init__(self, table: str, detail: str):
        message = f"Erreur lors de la recherche en base pour la table {table}: {detail}"
        super().__init__(message, error_code=ErrorCode.DATABASE_ERROR)


# Functional Exceptions
class DataNotFound(FunctionalException):
    """
    Exception thrown when one or more data items cannot be found.

    Args:
        param_fields (str | dict[str, str] | list[dict[str, str]]):
            - A string for a single missing field.
            - A dictionary {field_name: value} for specific missing data.
            - A list of these formats.
    """

    def __init__(self, param_fields: str | dict[str, str] | list[dict[str, str]]):
        if isinstance(param_fields, str):
            formatted_message = (
                f"La donnée spécifiée est introuvable pour : {param_fields}"
            )
        elif isinstance(param_fields, dict):
            formatted_message = f"La donnée spécifiée est introuvable pour : {self._format_dict(param_fields)}"
        elif isinstance(param_fields, list):
            formatted_message = (
                "La donnée spécifiée est introuvable pour : "
                + " | ".join(
                    self._format_dict(entry) if isinstance(entry, dict) else entry
                    for entry in param_fields
                )
            )
        else:
            raise ValueError(
                "param_fields doit être une chaîne, un dictionnaire ou une liste de dictionnaires"
            )

        super().__init__(formatted_message, error_code=ErrorCode.MISSING_DATA)
        self.param_fields = param_fields

    @staticmethod
    def _format_dict(entry: dict[str, str]) -> str:
        """Formats a dictionary into a readable message."""
        return ", ".join(f"{key} : {value}" for key, value in entry.items())


class DataAlreadyExist(FunctionalException):
    """
    Exception thrown when the specified data already exists.

    Args:
        param_fields (str | dict[str, str]):
            - A string for a single field.
            - A dictionary where keys are the fields and values are the corresponding data values.
    """

    def __init__(self, param_fields: str | dict[str, str]):
        if isinstance(param_fields, str):
            formatted_message = f"Cet élément existe déjà : {param_fields}"
        elif isinstance(param_fields, dict):
            formatted_message = "Cet élément existe déjà : " + ", ".join(
                f"{key} avec valeur {value}" for key, value in param_fields.items()
            )
        else:
            error_message = "param doit être une chaîne ou un dictionnaire de chaînes"
            raise ValueError(error_message)

        super().__init__(formatted_message, error_code=ErrorCode.DATA_ALREADY_EXIST)
        self.param = param_fields


class MissingData(FunctionalException):
    """
    Exception thrown when one or more required data fields are missing.

    param:
        param_fields: List of missing data fields.
    """

    def __init__(self, param_fields: list[str]):
        formatted_message = (
            f"Certaines data sont manquantes : {', '.join(param_fields)}"
        )
        super().__init__(formatted_message, error_code=ErrorCode.MISSING_DATA)
        self.param_fields = param_fields


class MissingParameter(FunctionalException):
    """
    Exception thrown when one or more required parameters are missing.

    param:
        param_fields: Parameter or list of missing parameters.
    """

    def __init__(self, param_fields: str | list[str]):
        message = f"Certaines data sont manquantes : {', '.join(param_fields) if isinstance(param_fields, list) else param_fields}"
        super().__init__(message, error_code=ErrorCode.MISSING_PARAMETER)
        self.param_fields = param_fields


class TemplateNotFound(FunctionalException):
    """
    Exception thrown when no valid template is found.
    """

    def __init__(self):
        message = "Aucun template trouvé."
        super().__init__(message, ErrorCode.NO_TEMPLATE_FOUND)


class NoMatchingAction(FunctionalException):
    """
    Exception thrown when no corresponding action is found for an API request.
    This exception could be a true error (exact_message=True) or a in case if we want to return a generic leonard message (exact_message=False).
    """

    def __init__(self, detail: str = None, exact_message: bool = False):
        message = 'v message to tell context'
        super().__init__(
            message, ErrorCode.NO_MATCHING_ACTION, exact_message=exact_message
        )
        self.detail = detail


class FileGenerationException(FunctionalException):
    """
    Exception thrown when an error occurs during file generation.

    param:
        format: Format of the file for which the error occurred.
        file_info: Dictionary, list, or string containing details about the file(s) that caused the error.
    """

    def __init__(self, format: str, file_info: dict[str, str] | str = None):
        if isinstance(file_info, dict):
            file_info_msg = " avec les informations suivantes : " + ", ".join(
                f"{key} : {value}" for key, value in file_info.items()
            )
        elif isinstance(file_info, str):
            file_info_msg = f" avec les informations suivantes : {file_info}"
        else:
            file_info_msg = ""
        message = f"Une erreur est survenue lors de la génération du fichier en format {format}{file_info_msg}."
        super().__init__(message, ErrorCode.FILE_GENERATION_ERROR)
        self.format = format
        self.file_info = file_info


class ParsingException(FunctionalException):
    """
    Exception thrown when an error occurs during information extraction.

    param:
        param_fields: Parameters or fields for which extraction failed.
    """

    def __init__(self, param_fields: str | list[str]):
        message = f"Extraction d'information impossible : {', '.join(param_fields) if isinstance(param_fields, list) else param_fields}"
        super().__init__(message, ErrorCode.PARSING_EXCEPTION)
        self.param = param_fields


class NoResponse(FunctionalException):
    """
    Exception thrown when no usable response is returned by an agent.
    """

    def __init__(self, detail: str = None):
        message = "L'agent n'a retourné aucune réponse exploitable."
        super().__init__(message, ErrorCode.NO_RESPONSE)
        self.detail = detail


class FormatException(FunctionalException):
    """
    Exception thrown when there is a problem with the format or structure of a response.

    Args:
        error_type (str): Type of error ('json', 'key', etc.).
    """

    def __init__(self, error_type: str = None):
        # Message personnalisé en fonction de l'erreur
        if error_type == "json":
            message = "Erreur JSON dans la réponse OpenAI."
        elif error_type == "key":
            message = "Erreur de structure dans la réponse OpenAI, clé manquante."
        else:
            message = (
                "Erreur de format ou de structure inconnue dans la réponse OpenAI."
            )

        super().__init__(message, error_code=ErrorCode.FORMAT_ERROR)
        self.error_type = error_type


class ErrorResponseGPT(FunctionalException):
    """
    Exception thrown when chatGPT write the error key in his response

    Args:
        action (str): action aimed by the error
        detail (str): details gave by chatGPT on the error
    """

    def __init__(self, action: str, detail: str):
        message = f"? OpenAI n'a pas réussi à traiter {action}: {detail}"
        super().__init__(
            message, error_code=ErrorCode.CHATGPT_RESPONSE_ERROR, exact_message=False
        )


class NoResourceAccess(FunctionalException):
    """
    Exception thrown when the user does not have access to the ressource
    """

    def __init__(self, detail: str | None = None):
        message = detail
        if message is None:
            message = "Vous n'avez pas les droits suffisant pour accéder à la ressource demandée"
        super().__init__(
            message, error_code=ErrorCode.NO_RESOURCE_ACCESS, exact_message=False
        )


class NoEmployeeIdException(FunctionalException):
    """
    Exception thrown when there is several names in the response
    """

    def __init__(self, id: str):
        message = f"Je n'ai pas trouvé d'information concernant {id}, assurez vous que cette personne est bien un collaborateur. Si c'est le cas veuillez contacter votre administrateur."
        super().__init__(
            message, error_code=ErrorCode.NO_EMPLOYEE_ID_ERROR, exact_message=False
        )


class SeveralEmployeesIdException(FunctionalException):
    """
    Exception thrown when there is several names in the response
    """

    def __init__(self):
        message = "Je ne peux traiter de demande que sur un seul employé à la fois. Merci de faire plusieurs demandes si vous souhaitez des informations sur différentes personnes."
        super().__init__(
            message,
            error_code=ErrorCode.SEVERAL_EMPLOYEES_IDS_ERROR,
            exact_message=False,
        )


class UnknownEntity(FunctionalException):
    """
    Exception thrown when the user's entity is not known or add missing attribues.

    Args:
        message (str): error message
    """

    def __init__(self, detail: str):
        message = f"Je ne connais pas l'entité {detail}. Si vous pensez que cela n'est pas normal vous pouvez contacter votre administrateur."
        super().__init__(
            message, error_code=ErrorCode.MISSING_DATA, exact_message=False
        )


class UnknownEmployee(FunctionalException):
    """
    Exception thrown when the employee asked by the user is unknown in base.

    Args:
        message (str): error message
    """

    def __init__(self, detail: str):
        message = f"Je ne trouve pas d'information concernant {detail} dans notre base de donnée. Assurez vous que cette personne est bien un collaborateur."
        super().__init__(
            message, error_code=ErrorCode.MISSING_DATA, exact_message=False
        )

    # UnknownEmployee


class HrProfile(UnknownEmployee):
    """
    Exception thrown when the employee asked has no HR File in the DB

    Args:
        detail (str): data asked for
    """

    def __init__(self, detail: str):
        message = f"Je ne trouve pas de fiche RH pour {detail} dans les données disponibles. Assurez-vous que le nom et le prénom sont correctement écrits ou que la personne que vous recherchez est bien dans la base de données."
        super().__init__(message)
        self.detail = detail


# Generic Exception


class UnexpectedException(GenericException):
    """
    Exception thrown when an unknown or unhandled error occurs.
    """

    def __init__(self, detail: str = None):
        message = f"Une erreur inconnue est survenue : {detail}."
        super().__init__(
            message,
            status_code=ErrorCode.UNEXPECTED_ERROR.value,
            error_code=ErrorCode.UNEXPECTED_ERROR,
        )


class NoEntity(GenericException):
    """
    Exception when the employee is not associated with any entity.
    """

    def __init__(self):
        message = "Impossible d'afficher la fiche contact RH. La personne recherchée n'est rattachée à aucune entité. Veuillez vérifier les informations saisies ou contacter le support RH pour plus d’assistance."
        super().__init__(
            message,
            status_code=ErrorCode.NO_ENTITY.value,
            error_code=ErrorCode.NO_ENTITY,
        )
