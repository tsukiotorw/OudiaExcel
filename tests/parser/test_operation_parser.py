"""
Operation Parserのテスト
"""
from src.parser.operation_parser import (
    OperationParser,
    OperationParserError,
)
from src.models.operation import (
    ConnectDetail,
    JunctionDetail,
    NumberChangeDetail,
    OperationType,
    OuterDetail,
    OutInDetail,
    ReleaseDetail,
    ShuntDetail,
)


def test_parse_single_junction() -> None:
    """
    ネストなしの単純なJunctionを解析できること。
    """
    parser = OperationParser()

    records = parser.parse([
        ("Operation71B", "5/$"),
    ])

    assert len(records) == 1

    record = records[0]

    assert record.order == 71
    assert record.is_before is True
    assert len(record.operations) == 1

    operation = record.operations[0]

    assert operation.type is OperationType.JUNCTION
    assert isinstance(operation.detail, JunctionDetail)
    assert operation.detail.time is None
    assert operation.detail.value is None
    assert operation.before_children == []
    assert operation.after_children == []


def test_parse_release_with_junction_child() -> None:
    """
    解結(Release)の後、After側にJunctionの子作業が
    ネストして解析できること。
    """
    parser = OperationParser()

    records = parser.parse([
        ("Operation41B", "2/0$1/955"),
        ("Operation41B.0A", "5/$0"),
    ])

    assert len(records) == 1

    record = records[0]

    assert record.order == 41
    assert record.is_before is True
    assert len(record.operations) == 1

    release = record.operations[0]

    assert release.type is OperationType.RELEASE
    assert isinstance(release.detail, ReleaseDetail)
    assert release.detail.release_position == 0
    assert release.detail.release_count == 1
    assert release.detail.release_time == "955"

    # Before側の子は空、After側にJunctionがネストしていること
    assert release.before_children == []
    assert len(release.after_children) == 1

    junction = release.after_children[0]

    assert junction.type is OperationType.JUNCTION
    assert isinstance(junction.detail, JunctionDetail)
    assert junction.detail.value == "0"
    assert junction.before_children == []
    assert junction.after_children == []


def test_parse_connect_with_out_in_child() -> None:
    """
    複数作業(出区+増結)を含み、増結側(index=1)に
    出区(OutIn)の子作業がネストして解析できること。
    """
    parser = OperationParser()

    records = parser.parse([
        ("Operation36B", "3/502$/711,1/0$503"),
        ("Operation36B.1B", "3/502$/721"),
    ])

    assert len(records) == 1

    record = records[0]

    assert record.order == 36
    assert record.is_before is True
    assert len(record.operations) == 2

    out_operation, connect_operation = record.operations

    # 1件目: 出区
    assert out_operation.type is OperationType.OUT_IN
    assert isinstance(out_operation.detail, OutInDetail)
    assert out_operation.detail.time == "502"
    assert out_operation.detail.train_number == "711"
    assert out_operation.before_children == []
    assert out_operation.after_children == []

    # 2件目: 増結。Before側に出区の子作業がネストしている
    assert connect_operation.type is OperationType.CONNECT
    assert isinstance(connect_operation.detail, ConnectDetail)
    assert connect_operation.detail.connect_position == 0
    assert connect_operation.detail.connect_time == "503"

    assert len(connect_operation.before_children) == 1
    assert connect_operation.after_children == []

    nested_out = connect_operation.before_children[0]

    assert nested_out.type is OperationType.OUT_IN
    assert isinstance(nested_out.detail, OutInDetail)
    assert nested_out.detail.time == "502"
    assert nested_out.detail.train_number == "721"


def test_parse_release_with_shunt_and_junction_children() -> None:
    """
    解結(Release)のAfter側に、入換(Shunt)とJunctionの
    2件がネストして解析できること。
    """
    parser = OperationParser()

    records = parser.parse([
        ("Operation19B", "2/1$1/529"),
        ("Operation19B.0A", "0/8$531/540$0,5/$0"),
    ])

    record = records[0]
    release = record.operations[0]

    assert release.type is OperationType.RELEASE
    assert len(release.after_children) == 2

    shunt, junction = release.after_children

    assert shunt.type is OperationType.SHUNT
    assert isinstance(shunt.detail, ShuntDetail)
    assert shunt.detail.linked_track_index == 8
    assert shunt.detail.departure_time == "531"
    assert shunt.detail.arrival_time == "540"
    assert shunt.detail.show_arrival is False

    assert junction.type is OperationType.JUNCTION
    assert isinstance(junction.detail, JunctionDetail)
    assert junction.detail.value == "0"


def test_parse_multiple_records_sorted_by_order_and_position() -> None:
    """
    複数のOperationRecordが (order, is_before) 順に
    ソートされて返されること。
    """
    parser = OperationParser()

    records = parser.parse([
        ("Operation3A", "6/ZZZ,5/$0"),
        ("Operation2B", "3/2359$/901"),
    ])

    assert len(records) == 2

    # order=2(Before)が先、order=3(After)が後になっていること
    assert records[0].order == 2
    assert records[0].is_before is True

    assert records[1].order == 3
    assert records[1].is_before is False

    number_change, junction = records[1].operations

    assert number_change.type is OperationType.NUMBER_CHANGE
    assert isinstance(number_change.detail, NumberChangeDetail)
    assert number_change.detail.train_number == "ZZZ"

    assert junction.type is OperationType.JUNCTION


def test_parse_outer_detail() -> None:
    """
    路線外始発(Outer)を解析できること。
    """
    parser = OperationParser()

    records = parser.parse([
        ("Operation41A", "4/0$533/602$"),
    ])

    operation = records[0].operations[0]

    assert operation.type is OperationType.OUTER
    assert isinstance(operation.detail, OuterDetail)
    assert operation.detail.outer_station_index == 0
    assert operation.detail.departure_time == "533"
    assert operation.detail.arrival_time == "602"


def test_parse_invalid_key_raises_error() -> None:
    """
    不正なOperationキー形式の場合、
    OperationParserErrorが送出されること。
    """
    parser = OperationParser()

    try:
        parser.parse([("InvalidKey", "5/$")])
        assert False, "OperationParserErrorが送出されるはず"
    except OperationParserError:
        pass


def test_parse_missing_root_for_nested_key_raises_error() -> None:
    """
    ネストキーに対応するルートキーが存在しない場合、
    OperationParserErrorが送出されること。
    """
    parser = OperationParser()

    try:
        parser.parse([("Operation41B.0A", "5/$0")])
        assert False, "OperationParserErrorが送出されるはず"
    except OperationParserError:
        pass
