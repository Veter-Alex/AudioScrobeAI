"""
Модуль для проверки здоровья базы данных и настроек приложения.

Этот модуль содержит функции для проверки подключения к базе данных,
существования таблиц, настроек окружения и других системных зависимостей.
"""

import logging
import os
import subprocess
import sys
from typing import Any, Dict, List

from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError

from src.database import Base, engine
from src.models.users import User

# Настройка логирования
logger = logging.getLogger(__name__)


class ApplicationHealthChecker:
    """
    Класс для комплексной проверки здоровья приложения.

    Проверяет базу данных, настройки окружения и системные зависимости.
    """

    def __init__(self) -> None:
        self.engine = engine
        self.required_env_vars = [
            "POSTGRES_DB",
            "POSTGRES_USER",
            "POSTGRES_PASSWORD",
            "DB_HOST",
            "SECRET_KEY",
            "DEBUG",
            "APP_ENV",
        ]

    def check_environment_variables(self) -> Dict[str, Any]:
        """
        Проверяет наличие и корректность переменных окружения.

        Returns:
            Dict[str, Any]: Результат проверки переменных окружения.
        """
        missing_vars = []
        empty_vars = []

        for var in self.required_env_vars:
            value = os.getenv(var)
            if value is None:
                missing_vars.append(var)
            elif not value.strip():
                empty_vars.append(var)

        result = {
            "status": "healthy",
            "message": "Все необходимые переменные окружения установлены",
            "details": {
                "required_vars": self.required_env_vars,
                "missing_vars": missing_vars,
                "empty_vars": empty_vars,
            },
        }

        if missing_vars or empty_vars:
            result["status"] = "unhealthy"
            messages = []
            if missing_vars:
                messages.append(f"Отсутствуют переменные: {', '.join(missing_vars)}")
            if empty_vars:
                messages.append(f"Пустые переменные: {', '.join(empty_vars)}")
            result["message"] = "; ".join(messages)

            logger.error(f"Проблемы с переменными окружения: {result['message']}")
        else:
            logger.info("Все переменные окружения корректно установлены")

        return result

    def check_database_connection(self) -> Dict[str, Any]:
        """
        Проверяет подключение к базе данных.

        Returns:
            Dict[str, Any]: Результат проверки подключения.
        """
        try:
            with self.engine.connect() as connection:
                # Выполняем простой запрос для проверки подключения
                result = connection.execute(text("SELECT 1 as test"))
                row = result.fetchone()
                if row and row[0] == 1:
                    logger.info("Подключение к базе данных успешно")
                    return {
                        "status": "healthy",
                        "message": "Подключение к базе данных работает корректно",
                        "details": {"connection_test": "passed"},
                    }
                else:
                    logger.error("Неожиданный результат тестового запроса")
                    return {
                        "status": "unhealthy",
                        "message": "Неожиданный результат тестового запроса",
                        "details": {"connection_test": "failed"},
                    }
        except SQLAlchemyError as e:
            logger.error(f"Ошибка подключения к базе данных: {str(e)}")
            return {
                "status": "unhealthy",
                "message": f"Ошибка подключения к базе данных: {str(e)}",
                "details": {"connection_test": "failed", "error": str(e)},
            }

    def check_database_tables(self) -> Dict[str, Any]:
        """
        Проверяет существование необходимых таблиц.

        Returns:
            Dict[str, Any]: Результат проверки таблиц.
        """
        try:
            inspector = inspect(self.engine)
            existing_tables = inspector.get_table_names()

            # Получаем список таблиц из моделей SQLAlchemy
            # Some Base subclasses may not be direct ORM mapped classes; filter those with __tablename__
            expected_tables = [
                table.__tablename__
                for table in Base.__subclasses__()
                if hasattr(table, "__tablename__")
            ]

            # Добавляем таблицы из других модулей, если они есть
            additional_tables: List[str] = []  # Например: ['alembic_version']

            all_expected = expected_tables + additional_tables

            missing_tables = [
                table for table in all_expected if table not in existing_tables
            ]
            extra_tables = [
                table for table in existing_tables if table not in all_expected
            ]

            result: Dict[str, Any] = {
                "status": "healthy" if not missing_tables else "warning",
                "message": f"Найдено {len(existing_tables)} таблиц",
                "details": {
                    "existing_tables": existing_tables,
                    "expected_tables": all_expected,
                    "missing_tables": missing_tables,
                    "extra_tables": extra_tables,
                },
            }

            if missing_tables:
                current_message = str(result["message"])
                result["message"] = (
                    current_message + f", отсутствуют: {', '.join(missing_tables)}"
                )
                logger.warning(f"Отсутствуют таблицы: {missing_tables}")
            else:
                logger.info("Все ожидаемые таблицы найдены")

            return result

        except SQLAlchemyError as e:
            logger.error(f"Ошибка при проверке таблиц: {str(e)}")
            return {
                "status": "unhealthy",
                "message": f"Ошибка при проверке таблиц: {str(e)}",
                "details": {"error": str(e)},
            }

    def check_database_permissions(self) -> Dict[str, Any]:
        """
        Проверяет права доступа к базе данных.

        Returns:
            Dict[str, Any]: Результат проверки прав доступа.
        """
        try:
            with self.engine.connect() as connection:
                # Проверяем возможность создания временной таблицы
                connection.execute(
                    text("CREATE TEMP TABLE test_permissions (id SERIAL PRIMARY KEY)")
                )
                connection.execute(text("INSERT INTO test_permissions DEFAULT VALUES"))
                connection.execute(text("DROP TABLE test_permissions"))
                connection.commit()

                logger.info("Права доступа к базе данных в порядке")
                return {
                    "status": "healthy",
                    "message": "Права доступа к базе данных достаточны",
                    "details": {"permissions_test": "passed"},
                }

        except SQLAlchemyError as e:
            logger.error(f"Недостаточно прав доступа: {str(e)}")
            return {
                "status": "unhealthy",
                "message": f"Недостаточно прав доступа: {str(e)}",
                "details": {"permissions_test": "failed", "error": str(e)},
            }

    def check_and_create_superadmin(self) -> Dict[str, Any]:
        """
        Проверяет наличие пользователя superadmin и создает его при необходимости.

        Returns:
            Dict[str, Any]: Результат проверки/создания superadmin пользователя.
        """
        try:
            # Используем контекстный менеджер для сессии
            from sqlalchemy.orm import sessionmaker

            SessionLocal = sessionmaker(
                autocommit=False, autoflush=False, bind=self.engine
            )

            with SessionLocal() as session:
                # Проверяем существование superadmin пользователя
                superadmin = (
                    session.query(User)
                    .filter(User.username == "superadmin", User.is_admin)
                    .first()
                )

                if superadmin is not None:
                    logger.info("Пользователь superadmin уже существует")
                    return {
                        "status": "healthy",
                        "message": "Пользователь superadmin уже существует",
                        "details": {
                            "superadmin_exists": True,
                            "user_id": superadmin.id,
                            "action_taken": "none",
                        },
                    }

                # Создаем нового superadmin пользователя
                logger.info("Создаем пользователя superadmin...")
                # Create User without passing unexpected kwargs to avoid mypy/call-arg issues
                new_superadmin = User()
                new_superadmin.username = "superadmin"
                new_superadmin.is_admin = True
                new_superadmin.set_password("superadmin")

                session.add(new_superadmin)
                session.commit()
                session.refresh(new_superadmin)

                logger.info(
                    f"Пользователь superadmin успешно создан с ID: {new_superadmin.id}"
                )
                return {
                    "status": "healthy",
                    "message": "Пользователь superadmin успешно создан",
                    "details": {
                        "superadmin_exists": False,
                        "user_id": new_superadmin.id,
                        "action_taken": "created",
                    },
                }

        except SQLAlchemyError as e:
            logger.error(f"Ошибка при работе с пользователем superadmin: {str(e)}")
            return {
                "status": "unhealthy",
                "message": f"Ошибка при работе с пользователем superadmin: {str(e)}",
                "details": {"error": str(e), "action_taken": "failed"},
            }
        except Exception as e:
            logger.error(f"Неожиданная ошибка при проверке superadmin: {str(e)}")
            return {
                "status": "unhealthy",
                "message": f"Неожиданная ошибка при проверке superadmin: {str(e)}",
                "details": {"error": str(e), "action_taken": "failed"},
            }

    def check_application_settings(self) -> Dict[str, Any]:
        """
        Проверяет корректность настроек приложения.

        Returns:
            Dict[str, Any]: Результат проверки настроек.
        """
        issues = []

        # Проверяем APP_ENV
        app_env = os.getenv("APP_ENV", "").lower()
        if app_env not in ["development", "production", "testing"]:
            issues.append(
                f"Некорректное значение APP_ENV: '{app_env}' (должно быть development/production/testing)"
            )

        # Проверяем SECRET_KEY
        secret_key = os.getenv("SECRET_KEY", "")
        if len(secret_key) < 32:
            issues.append("SECRET_KEY слишком короткий (минимум 32 символа)")

        # Проверяем DEBUG
        debug = os.getenv("DEBUG", "").lower()
        if debug not in ["true", "false"]:
            issues.append(
                f"Некорректное значение DEBUG: '{debug}' (должно быть true/false)"
            )

        result = {
            "status": "healthy" if not issues else "warning",
            "message": (
                "Настройки приложения корректны"
                if not issues
                else f"Найдены проблемы с настройками: {len(issues)}"
            ),
            "details": {
                "issues": issues,
                "settings_checked": ["APP_ENV", "SECRET_KEY", "DEBUG"],
            },
        }

        if issues:
            logger.warning(f"Проблемы с настройками приложения: {issues}")
        else:
            logger.info("Настройки приложения корректны")

        return result

    def run_database_migrations(self) -> Dict[str, Any]:
        """
        Автоматически запускает миграции базы данных с помощью Alembic.

        Returns:
            Dict[str, Any]: Результат выполнения миграций.
        """
        try:
            logger.info("Запуск миграций базы данных...")

            # Получаем путь к корневой директории проекта
            project_root = os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )

            # Запускаем команду alembic upgrade head
            result = subprocess.run(
                [sys.executable, "-m", "alembic", "upgrade", "head"],
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=300,  # 5 минут таймаут
            )

            if result.returncode == 0:
                logger.info("Миграции базы данных выполнены успешно")
                return {
                    "status": "healthy",
                    "message": "Миграции базы данных выполнены успешно",
                    "details": {"migration_output": result.stdout.strip()},
                }
            else:
                logger.error(f"Ошибка выполнения миграций: {result.stderr}")
                return {
                    "status": "unhealthy",
                    "message": f"Ошибка выполнения миграций: {result.stderr}",
                    "details": {
                        "migration_output": result.stdout.strip(),
                        "error_output": result.stderr.strip(),
                    },
                }

        except subprocess.TimeoutExpired:
            logger.error("Таймаут выполнения миграций")
            return {
                "status": "unhealthy",
                "message": "Таймаут выполнения миграций (5 минут)",
                "details": {"error": "timeout"},
            }
        except Exception as e:
            logger.error(f"Неожиданная ошибка при выполнении миграций: {str(e)}")
            return {
                "status": "unhealthy",
                "message": f"Неожиданная ошибка при выполнении миграций: {str(e)}",
                "details": {"error": str(e)},
            }

    def ensure_database_ready(self) -> Dict[str, Any]:
        """
        Гарантирует готовность базы данных, автоматически запуская миграции при необходимости.

        Returns:
            Dict[str, Any]: Результат подготовки базы данных.
        """
        logger.info("Проверяем готовность базы данных...")

        # Сначала проверяем подключение
        connection_check = self.check_database_connection()
        if connection_check["status"] != "healthy":
            return {
                "status": "unhealthy",
                "message": "Невозможно подключиться к базе данных",
                "details": connection_check,
            }

        # Проверяем таблицы
        tables_check = self.check_database_tables()
        if tables_check["status"] == "healthy":
            logger.info("База данных готова к работе")
            return {
                "status": "healthy",
                "message": "База данных готова к работе",
                "details": {"action_taken": "none"},
            }

        # Если таблицы отсутствуют, запускаем миграции
        if (
            tables_check["status"] == "warning"
            and tables_check["details"]["missing_tables"]
        ):
            logger.info(
                f"Обнаружены отсутствующие таблицы: {tables_check['details']['missing_tables']}"
            )
            logger.info("Запускаем миграции для создания таблиц...")

            migration_result = self.run_database_migrations()
            if migration_result["status"] == "healthy":
                # Проверяем таблицы еще раз после миграций
                final_check = self.check_database_tables()
                if final_check["status"] == "healthy":
                    return {
                        "status": "healthy",
                        "message": "База данных подготовлена успешно с помощью миграций",
                        "details": {
                            "action_taken": "migrations_run",
                            "migration_result": migration_result,
                        },
                    }
                else:
                    return {
                        "status": "unhealthy",
                        "message": "Миграции выполнены, но таблицы все еще отсутствуют",
                        "details": {
                            "action_taken": "migrations_run",
                            "migration_result": migration_result,
                            "final_check": final_check,
                        },
                    }
            else:
                return {
                    "status": "unhealthy",
                    "message": "Не удалось выполнить миграции базы данных",
                    "details": {
                        "action_taken": "migrations_failed",
                        "migration_result": migration_result,
                    },
                }

        # Если статус unhealthy (ошибка подключения к БД)
        return {
            "status": "unhealthy",
            "message": "База данных не готова к работе",
            "details": tables_check,
        }

    def perform_full_health_check(self) -> Dict[str, Any]:
        """
        Выполняет полную проверку здоровья приложения.

        Returns:
            Dict[str, Any]: Полный отчет о состоянии приложения.
        """
        logger.info("Начинаем полную проверку здоровья приложения")

        results: Dict[str, Any] = {
            "overall_status": "healthy",
            "checks": {
                "environment": self.check_environment_variables(),
                "database_connection": self.check_database_connection(),
                "database_tables": self.check_database_tables(),
                "database_permissions": self.check_database_permissions(),
                "superadmin_user": self.check_and_create_superadmin(),
                "application_settings": self.check_application_settings(),
            },
        }

        # Определяем общий статус
        checks_dict = results["checks"]
        if isinstance(checks_dict, dict):
            for check_name, check_result in checks_dict.items():
                if (
                    isinstance(check_result, dict)
                    and check_result.get("status") == "unhealthy"
                ):
                    results["overall_status"] = "unhealthy"
                    break
                elif (
                    isinstance(check_result, dict)
                    and check_result.get("status") == "warning"
                    and results["overall_status"] == "healthy"
                ):
                    results["overall_status"] = "warning"

        logger.info(
            f"Проверка здоровья завершена. Общий статус: {results['overall_status']}"
        )
        return results

    def get_health_summary(self) -> str:
        """
        Возвращает краткую сводку состояния здоровья.

        Returns:
            str: Краткая сводка.
        """
        full_check = self.perform_full_health_check()
        status = full_check["overall_status"]

        if status == "healthy":
            return "✅ Приложение готово к работе"
        elif status == "warning":
            return "⚠️  Приложение работает, но есть предупреждения"
        else:
            return "❌ Приложение не готово к работе"


def check_application_health() -> bool:
    """
    Быстрая функция для проверки здоровья приложения.

    Returns:
        bool: True если приложение здорово, False в противном случае.
    """
    checker = ApplicationHealthChecker()
    result = checker.perform_full_health_check()
    overall_status = str(result.get("overall_status", ""))
    return overall_status == "healthy"


def ensure_application_ready() -> None:
    """
    Гарантирует готовность приложения к работе.

    Автоматически подготавливает базу данных при необходимости.
    Вызывает исключение, если приложение не готово.
    """
    logger.info("Проверяем готовность приложения...")

    checker = ApplicationHealthChecker()

    # Сначала проверяем переменные окружения
    env_check = checker.check_environment_variables()
    if env_check["status"] != "healthy":
        logger.error(f"Проблемы с переменными окружения: {env_check['message']}")
        raise RuntimeError(f"Приложение не готово к работе: {env_check['message']}")

    # Проверяем настройки приложения
    settings_check = checker.check_application_settings()
    if settings_check["status"] == "unhealthy":
        logger.error(f"Проблемы с настройками приложения: {settings_check['message']}")
        raise RuntimeError(
            f"Приложение не готово к работе: {settings_check['message']}"
        )

    # Подготавливаем базу данных (автоматически запускает миграции при необходимости)
    db_ready_result = checker.ensure_database_ready()
    if db_ready_result["status"] != "healthy":
        logger.error(f"База данных не готова: {db_ready_result['message']}")
        raise RuntimeError(
            f"Приложение не готово к работе: {db_ready_result['message']}"
        )

    # Финальная проверка здоровья
    if not check_application_health():
        raise RuntimeError("Приложение не готово к работе после всех проверок.")

    logger.info("Приложение готово к работе")


def print_health_report() -> None:
    """
    Выводит подробный отчет о состоянии здоровья приложения.
    """
    checker = ApplicationHealthChecker()
    result = checker.perform_full_health_check()

    print("\n" + "=" * 60)
    print("ОТЧЕТ О ЗДОРОВЬЕ ПРИЛОЖЕНИЯ")
    print("=" * 60)

    status_emoji = {"healthy": "✅", "warning": "⚠️ ", "unhealthy": "❌"}

    checks_dict = result.get("checks", {})
    if isinstance(checks_dict, dict):
        for check_name, check_result in checks_dict.items():
            if isinstance(check_result, dict):
                emoji = status_emoji.get(check_result.get("status", ""), "❓")
                print(f"\n{emoji} {check_name.upper()}:")
                print(f"   Статус: {check_result.get('status', 'unknown')}")
                print(f"   Сообщение: {check_result.get('message', 'no message')}")

                details = check_result.get("details")
                if isinstance(details, dict):
                    if "missing_vars" in details and details["missing_vars"]:
                        print(
                            f"   Отсутствующие переменные: {', '.join(details['missing_vars'])}"
                        )
                    if "empty_vars" in details and details["empty_vars"]:
                        print(
                            f"   Пустые переменные: {', '.join(details['empty_vars'])}"
                        )
                    if "issues" in details and details["issues"]:
                        for issue in details["issues"]:
                            print(f"   • {issue}")

    overall_status = str(result.get("overall_status", "unknown"))
    print("\n" + "=" * 60)
    print(
        f"ОБЩИЙ СТАТУС: {status_emoji.get(overall_status, '❓')} {overall_status.upper()}"
    )
    print("=" * 60 + "\n")
