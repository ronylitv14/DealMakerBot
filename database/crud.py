import asyncio
import decimal
from datetime import datetime
from typing import List, Any, Optional, Union
import enum
from asyncpg.exceptions import InvalidAuthorizationSpecificationError

from sqlalchemy import select, update, delete, or_, desc, and_
from sqlalchemy.dialects.postgresql import insert, array
from sqlalchemy.exc import (
    IntegrityError, DataError, InvalidRequestError, NoResultFound

)

from database.database import async_session
from database.models import (User, TaskStatus, Task, GroupMessage, Balance, Executor, PropositionBy, WithdrawalStatus,
                             WithdrawalRequest, FileType, Chat, Transaction, TransactionStatus, TransactionType,
                             ProfileStatus, Warning, UserStatus)

from database.models import TicketStatus, UserTicket

from uuid import uuid1

COMMISSION = decimal.Decimal("0.03")


class BalanceAction(enum.Enum):
    replenishment: str = "replenishment"
    withdrawal: str = "withdrawal"


class UserType(enum.Enum):
    client: str = "Client"
    executor: str = "Executor"


# Users utils
async def get_user_auth(telegram_id: int) -> User:
    try:
        async with async_session() as session:
            res = await session.execute(select(User).where(User.telegram_id == telegram_id))

        return res.scalars().first()
    except IntegrityError as err:
        print(err)
    finally:
        await session.close()


async def get_executor_auth(telegram_id: int):
    try:
        async with async_session() as session:
            res = await session.execute(select(Executor).where(Executor.user_id == telegram_id))

        return res.scalars().first()
    except IntegrityError:
        await session.rollback()
        print("Something wrong with db")
    finally:
        await session.close()


async def delete_user_from_db(
        user_id: int
):
    try:
        async with async_session() as session:
            await session.execute(
                delete(User).where(User.telegram_id == user_id)
            )
            await session.commit()
    except IntegrityError:
        await session.rollback()
        raise
    except Exception as e:
        print(e)
    finally:
        await session.close()


async def save_user_to_db(
        telegram_id: int,
        username: str,
        phone: str,
        password: str,
        chat_id: int,
        tg_username: str,
        email: str = "",
):
    try:
        async with async_session() as session:
            user = User(
                tg_id=telegram_id,
                username=username,
                phone=phone,
                email=email,
                password=password,
                chat_id=chat_id,
                tg_username=tg_username
            )

            session.add(user)
            await session.commit()
            await session.close()
        return True
    except IntegrityError:
        await session.rollback()
        print("IntegrityError: Violated a database constraint.")
    except DataError:
        await session.rollback()
        print("DataError: Invalid data type or value.")
    except InvalidRequestError:
        await session.rollback()
        print("InvalidRequestError: The session is in an invalid state.")
    finally:
        await session.close()
    return False


async def _update_user_field(user_id: int, field_name: str, value: str) -> None:
    """
    Update a specific field for a user in the database.

    Parameters:
    - user_id: The ID of the user.
    - field_name: The name of the field to update.
    - value: The new value for the field.

    Returns:
    None
    """
    try:
        async with async_session() as session:
            await session.execute(update(User).where((User.telegram_id == user_id)).values(**{field_name: value}))
            await session.commit()

    except IntegrityError:
        await session.rollback()
        print(f"IntegrityError: Violated a database constraint while updating {field_name}.")
    finally:
        await session.close()


async def update_user_email(
        user_id: int,
        email: str
):
    await _update_user_field(user_id, "email", email)


async def update_user_nickname(
        user_id: int,
        nickname: str
):
    await _update_user_field(user_id, "username", nickname)


async def update_user_phone(
        user_id: int,
        phone: str
):
    await _update_user_field(user_id, "phone", phone)


# Tasks cruds
async def save_task_to_db(
        client_id: int,
        status: TaskStatus,
        price: str,
        subjects: List[str],
        work_type: List[str],
        deadline: datetime.date = datetime.utcnow(),
        files: List[str] = None,
        files_type: List[FileType] = None,
        description: str = "",
        proposed_by=PropositionBy.public,
        executor_id: Optional[int] = None
):
    try:
        async with async_session() as session:
            task = Task(
                client_id=client_id,
                status=status,
                price=price,
                deadline=deadline,
                files=files,
                files_type=files_type,
                subjects=subjects,
                description=description,
                work_type=work_type,
                proposed_by=proposed_by,
                executor_id=executor_id
            )

            session.add(task)
            await session.commit()
            return task
    except AttributeError:
        await session.rollback()
        print("IntegrityError: Violated a database constraint. Task created")

    finally:
        await session.close()


async def update_task_files(files: List[str], task_id: int):
    try:
        async with async_session() as session:
            task = await session.execute(
                select(Task).where(Task.task_id == task_id)
            )
            task = task.scalars().first()
            task.files = files
            await session.commit()
            return task
    except IntegrityError:
        await session.rollback()
        print("IntegrityError: Violated a database constraint. task updated")
    finally:
        await session.close()


async def update_task_status(
        task_id: int,
        status: TaskStatus
):
    try:
        async with async_session() as session:
            await session.execute(
                update(Task).where((Task.task_id == task_id)).values(status=status)
            )

            await session.commit()

            return True
    except IntegrityError:
        await session.rollback()
        print("IntegrityError: Violated a database constraint. task updated")
    finally:
        await session.close()


async def get_task(task_id: int):
    try:
        async with async_session() as session:
            task = await session.execute(
                select(Task).where(Task.task_id == task_id)
            )
            task = task.scalars().first()
            return task
    except NoResultFound:
        return []
    finally:
        await session.close()


async def add_group_message(
        group_message_id: int,
        task_id: int,
        message_text: str,
        has_files: bool = False
):
    try:
        async with async_session() as session:
            group_message = GroupMessage(
                group_message_id=group_message_id,
                task_id=task_id,
                message_text=message_text,
                has_files=has_files
            )

            session.add(group_message)
            await session.commit()
            return True
    except IntegrityError:
        await session.rollback()
        print("IntegrityError: Violated a database constraint. group message added")

    return False


async def get_group_message(
        task_id: int
):
    try:
        async with async_session() as session:
            group_message = await session.execute(
                select(GroupMessage).where(GroupMessage.task_id == task_id)
            )
            group_message = group_message.scalars().first()
            return group_message
    except IntegrityError:
        print("Error with database acquired!")
    finally:
        await session.close()


async def get_orders(
        user_id: int,
        user_type: UserType,
        *status: TaskStatus,
        task_id: Union[int, Any] = None,
):
    try:
        async with async_session() as session:
            if user_type == UserType.client:
                default_stmt = select(Task).where(
                    (Task.client_id == user_id) & (Task.status.in_(status))
                )

            if user_type == UserType.executor:
                default_stmt = select(Task).where(
                    (Task.executor_id == user_id) & (Task.status.in_(status))
                )

            if task_id:
                default_stmt.where(
                    Task.task_id == task_id
                )

            orders = await session.execute(default_stmt)

            orders = orders.scalars().all()
            return orders
    except IntegrityError:
        print("Error with database acquired!")

    finally:
        await session.close()


async def get_executor_orders(
        executor_id: int,
        *status: TaskStatus
):
    try:
        async with async_session() as session:
            stmt = select(Task).where(
                (Task.executor_id == executor_id) & (Task.status.in_(status))
            )

            orders = await session.execute(stmt)

            return orders.scalars().all()

    except IntegrityError:
        print("Error retrieving data!")
        await session.rollback()

    finally:
        await session.close()


async def get_executor(
        user_id: int
):
    try:
        async with async_session() as session:
            result = await session.execute(
                select(Executor).where(Executor.user_id == user_id)
            )

            return result.scalars().first()
    except IntegrityError:
        await session.rollback()
        print("Cant get executor!")

    finally:
        await session.close()


async def get_all_executors(*args):
    try:
        async with async_session() as session:
            result = await session.execute(
                select(User).join(Executor, User.telegram_id == Executor.user_id)
            )

            return result.scalars().all()
    except IntegrityError:
        print("Error with getting data!")
        await session.rollback()
    finally:
        await session.close()


# Balance and transactions

async def get_user_balance(user_id: int) -> Balance:
    try:
        async with async_session() as session:
            result = await session.execute(
                select(Balance).where(
                    Balance.user_id == user_id
                )
            )

            return result.scalars().first()
    except IntegrityError:
        await session.rollback()
    finally:
        await session.close()


async def create_user_balance(user_id: int):
    try:
        async with async_session() as session:
            session.add(
                Balance(
                    user_id=user_id,
                    balance_money=0.00,
                    user_cards=[]
                )
            )
            await session.commit()
    except IntegrityError:
        print("Error with adding user")
    finally:
        await session.close()


async def create_executor_profile(
        user_id: int,
        description: str,
        work_examples: List[str],
        work_files_type: List[FileType],
        tags: List[str]

):
    try:
        async with async_session() as session:
            session.add(
                Executor(
                    user_id=user_id,
                    description=description,
                    work_examples=work_examples,
                    work_files_type=work_files_type,
                    tags=tags
                )
            )

            await session.commit()

    except IntegrityError:
        await session.rollback()
        print("Error with adding executor")

    finally:
        await session.close()


async def update_user_cards(user_id: int, card: str):
    try:
        async with async_session() as session:

            # Use the distinct operator to ensure the card is not already in the array
            stmt = insert(Balance).values(user_id=user_id, user_cards=[card])

            do_update_stmt = stmt.on_conflict_do_update(
                index_elements=['user_id'],
                set_={
                    # Use the distinct operator to ensure the card is not already in the array
                    'user_cards': Balance.user_cards.op('||')(array([card], type_="CHAR"))
                },
                # Only perform the update if the card isn't already in the array
                where=(~Balance.user_cards.contains(array([card], type_="CHAR")))
            )

            await session.execute(do_update_stmt)
            await session.commit()

            return True
    except IntegrityError:
        print("Err")
        await session.rollback()
    finally:
        await session.close()

    return False


async def get_user_by_task_id(task_id: int):
    try:
        async with async_session() as session:
            stmt = (
                select(User)
                .select_from(User)
                .join(Task, User.telegram_id == Task.client_id)
                .where(Task.task_id == task_id)
            )

            result = await session.execute(stmt)
            user = result.scalars().first()
            return user

    except IntegrityError:
        await session.rollback()
        print("Error with getting user")
    finally:
        await session.close()


async def get_proposed_deals(
        proposed_by: PropositionBy,
        user_id: int
) -> List[Task]:
    try:
        async with async_session() as session:

            if proposed_by == PropositionBy.client:
                executor: Executor = await get_executor(user_id)

                result = await session.execute(
                    select(Task).where(
                        (Task.proposed_by == proposed_by) & (Task.status == TaskStatus.active) & (
                                Task.executor_id == executor.executor_id)
                    )
                )
                return result.scalars().all()

            result = await session.execute(
                select(Task).where(
                    (Task.proposed_by == proposed_by) & (Task.status == TaskStatus.active) & (
                            Task.client_id == user_id)
                )
            )

            return result.scalars().all()

    except IntegrityError:
        print("Couldnt get data back")
        await session.rollback()

    finally:
        await session.close()


from uuid import uuid1


async def save_chat_data(
        chat_id: int,
        task_id: int,
        group_name: str,
        invite_link: str,
        participants_count: int,
        client_id: int,
        executor_id: int,
        chat_admin: str
):
    try:
        async with async_session() as session:
            chat = Chat(
                chat_id=chat_id,
                task_id=task_id,
                group_name=group_name,
                invite_link=invite_link,
                participants_count=participants_count,
                client_id=client_id,
                executor_id=executor_id,
                chat_admin=chat_admin
            )

            session.add(chat)
            await session.commit()

            return chat
    except IntegrityError as err:
        await session.rollback()
        print(err)
        print("Problems with saving chat")

    finally:
        await session.close()


async def get_recent_clients(
        executor_id: int
) -> List[User]:
    try:
        async with async_session() as session:
            result = await session.execute(
                select(User)
                .join(Task, Task.client_id == User.telegram_id)
                .where(Task.executor_id == executor_id)
            )

            return result.scalars().all()

    except IntegrityError:
        await session.rollback()
    finally:
        await session.close()


async def get_chats_by_taskid(
        task_id: int
):
    try:
        async with async_session() as session:
            res = await session.execute(
                select(Chat).where(Chat.task_id == task_id)
            )

            return res.scalars().all()

    except IntegrityError:
        await session.rollback()

    finally:
        await session.close()


async def add_transaction_data(
        invoice_id: str,
        amount: decimal.Decimal,
        transaction_type: TransactionType,
        transaction_status: TransactionStatus,
        sender_id: Optional[int] = None,
        receiver_id: Optional[int] = None,
        task_id: Optional[int] = None,

):
    try:
        async with async_session() as session:
            session.add(
                Transaction(
                    invoice_id=invoice_id,
                    amount=amount,
                    transaction_type=transaction_type,
                    transaction_status=transaction_status,
                    task_id=task_id,
                    sender_id=sender_id,
                    receiver_id=receiver_id
                )
            )

            await session.commit()

    except IntegrityError as err:
        print(err)
        print("Transaction error")
        await session.rollback()

    finally:
        await session.close()


async def update_transaction_status(
        reference: str,
        new_status: TransactionStatus
):
    try:
        async with async_session() as session:
            await session.execute(
                update(Transaction).where(Transaction.reference == reference).values(transaction_status=new_status)
            )

            await session.commit()

    except IntegrityError:
        await session.rollback()
    finally:
        await session.close()


async def get_executor_applications(

):
    try:
        async with async_session() as session:
            result = await session.execute(
                select(Executor).where(Executor.profile_state == ProfileStatus.created)
            )

            return result.scalars().all()

    except IntegrityError:
        print("error")
        await session.rollback()

    finally:
        await session.close()


async def update_application_status(
        executor_id: int,
        new_profile_state: ProfileStatus
):
    try:
        async with async_session() as session:
            await session.execute(
                update(Executor).where(Executor.executor_id == executor_id).values(profile_state=new_profile_state)
            )

            await session.commit()

    except IntegrityError:
        await session.rollback()
        print("Wrong params for executor status updating")

    finally:
        await session.close()


async def get_usual_users():
    try:
        async with async_session() as session:

            result = await session.execute(
                select(User).where(~User.user_status.in_([UserStatus.superuser]))
            )

            return result.scalars().all()

    except IntegrityError:
        print("Error with results")

    finally:
        await session.close()


async def create_new_balance(
        user_id: int,
        new_amount: decimal.Decimal
):
    try:
        async with async_session() as session:
            await session.execute(
                update(Balance).where(Balance.user_id == user_id).values(balance_money=new_amount)
            )

            await session.commit()

    except IntegrityError:
        print("Unsuccessfully updated balance")


async def get_user_transactions(
        user_id: int
):
    try:
        async with async_session() as session:
            res = await session.execute(
                select(Transaction).where(or_(Transaction.receiver_id == user_id, Transaction.sender_id == user_id))
            )

            return res.scalars().all()

    except IntegrityError:
        print("Error")
    finally:
        await session.close()


async def create_withdrawal_request(
        user_id: int,
        amount: decimal.Decimal,
        commission: decimal.Decimal,
        status: WithdrawalStatus,
        payment_method: str
):
    try:
        async with async_session() as session:
            session.add(
                WithdrawalRequest(
                    user_id=user_id,
                    amount=amount,
                    status=status,
                    payment_method=payment_method,
                    commission=commission
                )
            )

            await session.commit()

    except IntegrityError as err:
        print(err)
        await session.rollback()

    finally:
        await session.close()


async def get_all_withdrawal_requests(
        status: WithdrawalStatus = WithdrawalStatus.pending
):
    try:
        async with async_session() as session:
            res = await session.execute(
                select(WithdrawalRequest)
                .where(WithdrawalRequest.status == status)
                .order_by(desc(WithdrawalRequest.request_date))
            )

            return res.scalars().all()

    except IntegrityError as err:
        print(err)
    finally:
        await session.close()


async def update_withdrawal_request(
        request_id: int,
        new_status: WithdrawalStatus,
        processed_time: datetime,
        admin_id: int
):
    try:
        async with async_session() as session:
            await session.execute(
                update(WithdrawalRequest).where(WithdrawalRequest.request_id == request_id).values(
                    status=new_status,
                    processed_date=processed_time,
                    admin_id=admin_id
                )
            )

            await session.commit()

    except IntegrityError as err:
        print(err)
        await session.rollback()

    finally:
        await session.close()


async def update_balance(
        user_id: int,
        amount: decimal.Decimal,
        action: BalanceAction
):
    try:
        async with async_session() as session:
            balance = await session.execute(
                select(Balance).where(Balance.user_id == user_id)
            )

            balance = balance.scalars().first()

            if action == BalanceAction.replenishment:
                balance.balance_money += amount
            elif action == BalanceAction.withdrawal:
                balance.balance_money -= amount

            await session.commit()

    except IntegrityError:
        await session.rollback()

    finally:
        await session.close()


async def create_obj_in_db(
        obj: Any
):
    try:
        async with async_session() as session:
            session.add(obj)
            await session.commit()

    except IntegrityError as err:
        print(err)
        await session.rollback()

    finally:
        await session.close()


async def update_ban_status(
        user_id: int,
        is_banned: bool
):
    try:
        async with async_session() as session:
            await session.execute(
                update(User).where(User.telegram_id == user_id).values(is_banned=is_banned)
            )

            await session.commit()

    except IntegrityError as err:
        print(err)
        await session.rollback()

    finally:
        await session.close()


async def create_user_ticket(
        user_id: int,
        description: str,
        subject: str
):
    try:
        async with async_session() as session:
            ticket = UserTicket(
                user_id=user_id,
                description=description,
                subject=subject
            )

            session.add(ticket)
            await session.commit()

    except IntegrityError as err:
        print(err)
        await session.rollback()

    finally:
        await session.close()


async def create_user_warning(
        user_id: int,
        reason: str,
        admin_id: int,
        warning_count: int
):
    try:
        async with async_session() as session:
            obj = Warning(
                user_id=user_id,
                reason=reason,
                issued_by=admin_id
            )

            session.add(obj)

            await session.execute(
                update(User).where(User.telegram_id == user_id).values(warning_count=warning_count + 1)
            )

            await session.commit()

    except IntegrityError as err:
        print(err)
        await session.rollback()

    finally:
        await session.close()


async def get_user_tickets(
        status: TicketStatus = TicketStatus.open
):
    try:
        async with async_session() as session:

            res = await session.execute(
                select(UserTicket).where(UserTicket.status == status)
            )

            return res.scalars().all()

    except IntegrityError as err:
        print(err)

    finally:
        await session.close()


async def update_ticket_status(
        ticket_id: int,
        new_status: TicketStatus,
        admin_id: int
):
    try:
        async with async_session() as session:
            await session.execute(
                update(UserTicket).where(UserTicket.ticket_id == ticket_id).values(
                    status=new_status,
                    updated_at=datetime.utcnow(),
                    responded_by=admin_id,

                )
            )

            await session.commit()

    except IntegrityError as err:
        print(err)
        await session.rollback()

    finally:
        await session.close()


async def get_chat_object(
        chat_id: int = None,
        db_chat_id: Optional = None
) -> Chat:
    try:
        async with async_session() as session:

            if db_chat_id:
                res = await session.execute(
                    select(Chat).where(Chat.id == db_chat_id)
                )
                return res.scalars().first()

            if not chat_id:
                raise IntegrityError

            res = await session.execute(
                select(Chat).where(Chat.chat_id == chat_id)
            )

            return res.scalars().first()

    except Exception as err:
        print(err)
        await session.rollback()


from aiogram.enums import ChatType


async def update_chat_status(
        chat_type: ChatType,
        supergroup_id: int,
        db_chat_id
):
    try:
        async with async_session() as session:
            await session.execute(
                update(Chat).where(Chat.id == db_chat_id).values(
                    chat_type=chat_type,
                    supergroup_id=supergroup_id
                )
            )

            await session.commit()
            return True
    except IntegrityError as err:
        print("Failed saving")
        print(err)

    return False


async def create_transaction_data(
        receiver_id: int,
        sender_id: int,
        task_id: int,
        amount: decimal.Decimal
):
    try:
        async with async_session() as session:

            sender_balance = await session.execute(
                select(Balance).where(Balance.user_id == sender_id)
            )

            sender_balance = sender_balance.scalars().first()

            if sender_balance.balance_money < amount:
                raise ValueError("Incorrect transaction amount")

            commission = amount * COMMISSION

            amount_after_commission = amount - commission
            sender_balance -= amount

            transaction = Transaction(
                task_id=task_id,
                invoice_id=str(uuid1()),
                transaction_type=TransactionType.transfer,
                receiver_id=receiver_id,
                sender_id=sender_id,
                transaction_status=TransactionStatus.pending,
                commission=commission,
                amount=amount_after_commission
            )

            session.add(transaction)

            await session.execute(
                update(Task).where(Task.task_id == task_id).values(
                    executor_id=receiver_id,
                    status=TaskStatus.executing
                )
            )

            await session.commit()
            return transaction
    except IntegrityError as err:
        print(err)
        await session.rollback()

    finally:
        await session.close()
    return False


async def check_successful_payment(
        task_id,
        receiver_id,
        sender_id
):
    try:
        async with async_session() as session:
            res = await session.execute(
                select(Transaction).where(
                    (Transaction.task_id == task_id) & (Transaction.sender_id == sender_id) & (
                            Transaction.receiver_id == receiver_id)
                )
            )

            return True if res.scalars().all() else False
    except IntegrityError as err:
        print(err)
        await session.rollback()


async def accept_done_offer(
        transaction_id,
        task_id,
        receiver_id,
        amount
):
    try:
        async with async_session() as session:
            await session.execute(
                update(Transaction).where(Transaction.transaction_id == transaction_id).values(
                    transaction_status=TransactionStatus.completed
                )
            )

            await session.execute(
                update(Task).where(Task.task_id == task_id).values(
                    status=TaskStatus.done
                )
            )

            receiver_balance = await session.execute(
                select(Balance).where(Balance.user_id == receiver_id)
            )

            receiver_balance: Balance = receiver_balance.scalars().first()
            receiver_balance.balance_money += amount

            await session.commit()

    except IntegrityError as err:
        print("Error")
        await session.rollback()
        raise


async def get_all_user_chats(
        client_id: int
):
    try:
        async with async_session() as session:
            res = await session.execute(
                select(Chat).where(Chat.client_id == client_id)
            )

            return res.scalars().all()

    except IntegrityError:
        print("Get all users")
        raise


async def update_group_title(
        db_chat_id,
        group_name
):
    try:
        async with async_session() as session:
            await session.execute(
                update(Chat).where(Chat.id == db_chat_id).values(
                    group_name=group_name
                )
            )

            await session.commit()
    except IntegrityError as err:
        print(err)
        await session.rollback()


from sqlalchemy.sql.expression import func


async def get_similarity_users(
        name: str,
        is_executor: bool = False

) -> List[User]:
    try:
        async with async_session() as session:
            default_stmt = (select(User)
                            .where(or_((func.word_similarity(User.username, name) > 0.25),
                                       func.word_similarity(User.telegram_username, name) > 0.25))
                            .where(~User.user_status.in_([UserStatus.admin])))

            if is_executor:
                default_stmt = default_stmt.where(User.telegram_id.in_(select(Executor.user_id)))
            res = await session.execute(default_stmt)

        return res.scalars().all()

    except IntegrityError as err:
        print(err)
