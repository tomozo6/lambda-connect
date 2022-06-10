# ------------------------------------------------------------------------------
# import modules
# ------------------------------------------------------------------------------
# 標準ライブラリ
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional
from xmlrpc.client import boolean


# ------------------------------------------------------------------------------
# Class & Function
# ------------------------------------------------------------------------------
@dataclass(frozen=True)
class DutyGroup():
    start_day: int
    end_day: int
    phone_numbers: list


@dataclass(frozen=True)
class DutyRoster():
    '''当番表クラス
    '''
    groups: list[DutyGroup]
    call_order: list[int]

    def get_duty_phone_numbers(self, order_number: int) -> Optional[list]:
        '''
        指定された順番の電話番号リストを返します。
        指定された順番が無い場合はNoneを返します。
        '''

        # コール順リストの要素数を超えたリクエストにはNoneを返す
        if order_number >= len(self.call_order):
            return None

        # 指定された順番の電話番号リストを返す
        return self.groups[self.call_order[order_number]].phone_numbers


# ------------------------------------------------------------------------------
# Function
# ------------------------------------------------------------------------------
def make_duty_groups(duty_groups_dict: dict) -> list[DutyGroup]:
    '''
    dictからlist[DutyGroup] を生成します。
    DutyGroup型に変換できるようなDict構造出ない場合は例外を発生させます。
    '''
    duty_groups = []

    # dictを旧フォーマット扱いでlist[DutyGroup]への変換を試みる
    try:
        for _, value in duty_groups_dict.items():
            duty_groups.append(
                DutyGroup(
                    value['start_day'],
                    value['end_day'],
                    value['phone_number']
                )
            )
    # 旧フォーマット扱いで例外が出た場合は新フォーマット扱いでlist[DutyGroup]への変換を試みる
    except Exception:
        try:
            for value in duty_groups_dict:
                duty_groups.append(
                    DutyGroup(
                        value['start_day'],
                        value['end_day'],
                        value['phone_number']
                    )
                )

        # 旧でも新でも変換できなければ例外を返す
        except Exception:
            raise Exception('DutyGroup format error.')

    return duty_groups


def make_duty_roster(duty_groups: list[DutyGroup], repeat_count: int, repeat_group_mode: boolean) -> DutyRoster:
    def _get_duty_index(duty_groups) -> Optional[int]:
        '''
        今日の日付と一致するgroupのindex数を返します。
        もし今日の日付にマッチするグループが1つも無い場合はNoneを返します。
        '''
        today = datetime.now(timezone(timedelta(hours=+9), 'JST'))

        for index, group in enumerate(duty_groups):
            if group.start_day <= today.day <= group.end_day:
                return index

        return None

    # ----------------------------------------------------------

    base_duty_index = _get_duty_index(duty_groups)

    # 日付に一致するグループが無い場合は、最初のグループ(index: 0)をリピートカウント分リストに詰めて返す
    if base_duty_index is None:
        return DutyRoster(duty_groups, ([0, ] * repeat_count))

    # リピートグループモードのリターン
    if repeat_group_mode:
        orders = []
        for _ in range(repeat_count):
            orders.append(base_duty_index)
        return DutyRoster(duty_groups, orders)

    # 通常モードのリターン
    else:
        group_len = len(duty_groups)
        orders = []

        for i in range(group_len * repeat_count):
            orders.append((i + base_duty_index) % group_len)

        return DutyRoster(duty_groups, orders)
