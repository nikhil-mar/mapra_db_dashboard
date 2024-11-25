from config import connect
import pandas as pd

conn = connect()
cur = conn.cursor()

cur.execute("""select id, gharane, last_name, family_size, gender , full_name, first_name_m, marital_last_name_m, marital_first_name_m from bpb_profile""")
source_data = cur.fetchall()

df = pd.DataFrame(source_data, columns=['id', 'gharane', 'lastName','family_size','gender', 'fullName', 'firstNameM', 'maritalLastNameM','maritalFirstNameM'])

# df["firstName"] = df["fullName"].str.split(" |-", expand=True)[0]
df["firstName"] = df.loc[:,'fullName'].str.split(" |-", expand=True)[0]

print(df)
# conn = connect()
# cur = conn.cursor()

# cur.execute("""with cte as (
# select id, gharane, gharane_id, first_name_m, last_name_m, birth_date, living_status, gender, pidhi, date_part('year',age(birth_date)) as age
# from bpb_profile
# where
# living_status = 'Living' and
# birth_date is not null)
# ,cte1 as (
#     select id, age as oldest_age, last_name_m, gender,
# 	row_number() over (partition by last_name_m,gender order by age desc) as rownums
# 	from cte
#     where age < 100
# ),
# cte2 as (
#     select * from cte1
#     where rownums = 1
# ),
# cte3 as (
# select distinct last_name_m from bpb_last_name
# )

# select tab.last_name_m, tab1.oldest_age, tab1.gender,
# tab2.first_name_m, tab2.last_name_m, tab2.gharane, tab2.gharane_id, tab2.pidhi

# from 
# cte3 tab
# left join cte2 tab1 on tab.last_name_m = tab1.last_name_m
# left join cte tab2 on tab1.id = tab2.id
# order by gender ,tab.last_name_m""")

# source_data = cur.fetchall()
# main_df = pd.DataFrame(source_data)


# cur.execute("""with cte as (
# select id, gharane, gharane_id, first_name_m, last_name_m, birth_date, living_status, gender, pidhi, date_part('year',age(birth_date)) as age
# from bpb_profile
# where
# living_status = 'Living' and
# birth_date is not null)
# ,cte1 as (
#     select id, age as smallest_age, last_name_m, gender,
# 	row_number() over (partition by last_name_m,gender order by age) as rownums
# 	from cte
#     where age < 100
# ),
# cte2 as (
#     select * from cte1
#     where rownums = 1
# ),
# cte3 as (
# select distinct last_name_m from bpb_last_name
# )

# select tab.last_name_m, tab1.smallest_age, tab1.gender,
# tab2.first_name_m, tab2.last_name_m, tab2.gharane, tab2.gharane_id, tab2.pidhi

# from 
# cte3 tab
# left join cte2 tab1 on tab.last_name_m = tab1.last_name_m
# left join cte tab2 on tab1.id = tab2.id
# order by gender ,tab.last_name_m""")
# source_data = cur.fetchall()
# main_df = pd.DataFrame(source_data)
# print(main_df)