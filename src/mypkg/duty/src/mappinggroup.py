# ------------------------------------------------------------------------------
# import modules
# ------------------------------------------------------------------------------
# 標準ライブラリ
from dataclasses import dataclass


# ------------------------------------------------------------------------------
# Class
# ------------------------------------------------------------------------------
@dataclass(frozen=True)
class MappingGroup():
    sns_topic_name: str
    phone_number_json_file: str


@dataclass(frozen=True)
class MappingGroups():
    groups: list[MappingGroup]

    def get_phone_number_json_file(self, sns_topic_name: str) -> str:
        '''
        SNSTopicに対応するjsonファイル名を返します。
        '''
        for g in self.groups:
            if g.sns_topic_name == sns_topic_name:
                return g.phone_number_json_file

        raise Exception('The specified "sns_topic_name" was not in this MappingGroups.')


# ------------------------------------------------------------------------------
# Function
# ------------------------------------------------------------------------------
def make_mapping_groups(groups_dict: dict) -> MappingGroups:
    '''
    DictからMappingGroups型に変換します。
    '''
    groups: list[MappingGroup] = []

    try:
        for g in groups_dict:
            groups.append(
                MappingGroup(
                    g['sns_topic_name'],
                    g['phone_number_json_file']
                )
            )
    except Exception:
        raise Exception('Can not convert to MappingGroups. Please check input data.')

    return MappingGroups(groups)
