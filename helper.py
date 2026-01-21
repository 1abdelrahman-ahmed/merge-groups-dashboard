import pandas as pd
import urllib.parse
import os

def load_data(): #sheet_id, sheet_name):
    sheet_id = os.getenv("SHEET_ID")
    sheet_name = os.getenv("SHEET_NAME", "Form Responses 1")
    encoded_sheet_name = urllib.parse.quote(sheet_name)
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={encoded_sheet_name}"
    df = pd.read_csv(url)
    df.drop(columns=['Timestamp'], inplace=True)
    return df

def grouped_data(df, keys):
    return (
        df.groupby(keys)
        .agg(
            mergeable_groups=(
                'Group (e.g. G1 *uppercase)',
                lambda s: ", ".join(s)
            ),
            groups_count=(
                'Group (e.g. G1 *uppercase)',
                'nunique'
            ),
            number_of_students=(
                'Number of Students (Mean)',
                'sum'
            )
        )
        .reset_index()
    )

GROUP_COL = 'Group (e.g. G1 *uppercase)'
STUD_COL  = 'Number of Students (Mean)'

def build_view(df, keys, threshold=5):
    per_group = (
        df.groupby(keys + [GROUP_COL])[STUD_COL]
        .sum()
        .reset_index(name="group_students")
    )

    small = per_group[per_group["group_students"] < threshold].copy()
    big   = per_group[per_group["group_students"] >= threshold].copy()

    big_view = big.rename(columns={GROUP_COL: "groups", "group_students": "number_of_students"})
    big_view["groups_count"] = 1
    big_view = big_view[keys + ["groups", "groups_count", "number_of_students"]]

    if len(small) > 0:
        small_view = (
            small.groupby(keys, dropna=False)
                .agg(
                    groups=(GROUP_COL, lambda s: ", ".join(pd.unique(s))),
                    groups_count=(GROUP_COL, "nunique"),
                    number_of_students=("group_students", "sum"),
                )
                .reset_index()
        )
        small_view = small_view[keys + ["groups", "groups_count", "number_of_students"]]
    else:
        small_view = pd.DataFrame(columns=keys + ["groups", "groups_count", "number_of_students"])

    view = pd.concat([small_view, big_view], ignore_index=True)
    view = view.sort_values(keys).reset_index(drop=True)
    return view

def merged_only(df):
    return df[df['groups_count'] > 1].reset_index(drop=True)