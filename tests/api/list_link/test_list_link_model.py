from sqlmodel import Session

from app.api.list_link.models import ListLinkService
from tests.factories import (
    get_list_link_factory,
    get_parents_list_factory,
    get_school_factory,
    get_user_factory,
)


def test_link_service_get_number_of_holders(session: Session):
    school = get_school_factory(session, name="School")

    alice = get_user_factory(session, name="Alice")
    bob = get_user_factory(session, name="Bob")
    charlie = get_user_factory(session, name="Charlie")

    session.flush()

    parent_list = get_parents_list_factory(
        session, list_name="Parents List", school_id=school.id
    )

    session.flush()

    # alice_link
    get_list_link_factory(
        session,
        user_id=alice.id,
        list_id=parent_list.id,
        school_id=school.id,
        status="leader",
    )

    # bob_link
    get_list_link_factory(
        session,
        user_id=bob.id,
        list_id=parent_list.id,
        school_id=school.id,
        status="holder",
    )

    # charlie_link
    get_list_link_factory(
        session,
        user_id=charlie.id,
        list_id=parent_list.id,
        school_id=school.id,
        status="substitute",
    )

    session.flush()

    service = ListLinkService()

    # Alice and Bob are holders, Charlie is a substitute
    assert service.get_number_of_holders(session, parent_list.id) == 2
    assert service.get_number_of_substitutes(session, parent_list.id) == 1

    assert service.get_leader_user_id_of_list(session, parent_list.id) == alice.id
