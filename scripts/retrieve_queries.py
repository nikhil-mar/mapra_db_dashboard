summary_sql = """
select id, gharane_id, gharane, first_name, last_name, full_name, gender, living_status, marital_status, father_id, birth_date, death_date, no_of_sons, no_of_daughters from bpb_profile"""

gharane_lastname = """
select distinct gharane, last_name, gharane_m, last_name_m from bpb_profile"""

age_group_sql = "select id, gharane, last_name, birth_date, death_date, living_status from bpb_profile"
country_state_sql = "select id, gharane, last_name, family_size, province_or_state, country, province_or_state_m, country_m from bpb_profile"
common_names_sql = "select id, gharane, last_name, family_size, gender , full_name, first_name, first_name_m, marital_last_name_m, marital_first_name_m from bpb_profile"

gharane_m = "select distinct gharane_number, gharane_name, gharane_name_m from bpb_gharane"

surnames_m = "select distinct last_name_m, last_name from bpb_last_name"

oldest_individual_sql = """with cte as (
select id, gharane_m, gharane, gharane_id, first_name_m, first_name, middle_name_m, middle_name, last_name_m, last_name, birth_date, living_status, gender, pidhi, date_part('year',age(birth_date)) as age
from bpb_profile
where
living_status = 'Living' and
birth_date is not null)
,cte1 as (
    select id, age as oldest_age, last_name_m, gender,
	row_number() over (partition by last_name_m,gender order by age desc) as rownums
	from cte
    where age < 100
),
cte2 as (
    select * from cte1
    where rownums = 1
),
cte3 as (
select distinct last_name_m from bpb_last_name
)

select tab.last_name_m, tab2.last_name, tab1.oldest_age, tab1.gender,
tab2.first_name_m, tab2.first_name, tab2.middle_name_m, tab2.middle_name, tab2.last_name_m, tab2.gharane_m, tab2.gharane, tab2.gharane_id, tab2.pidhi
from 
cte3 tab
left join cte2 tab1 on tab.last_name_m = tab1.last_name_m
left join cte tab2 on tab1.id = tab2.id
order by gender ,tab.last_name_m"""

youngest_individual_sql = """with cte as (
select id, gharane_m, gharane, gharane_id, first_name_m, first_name, middle_name_m, middle_name, last_name_m, last_name, birth_date, living_status, gender, pidhi, date_part('year',age(birth_date)) as age
from bpb_profile
where
living_status = 'Living' and
birth_date is not null)
,cte1 as (
    select id, age as smallest_age, last_name_m, gender,
	row_number() over (partition by last_name_m,gender order by age) as rownums
	from cte
    where age < 100
),
cte2 as (
    select * from cte1
    where rownums = 1
),
cte3 as (
select distinct last_name_m from bpb_last_name
)

select tab.last_name_m, tab2.last_name, tab1.smallest_age, tab1.gender,
tab2.first_name_m, tab2.first_name, tab2.middle_name_m, tab2.middle_name, tab2.last_name_m, tab2.gharane_m, tab2.gharane, tab2.gharane_id, tab2.pidhi

from 
cte3 tab
left join cte2 tab1 on tab.last_name_m = tab1.last_name_m
left join cte tab2 on tab1.id = tab2.id
order by gender ,tab.last_name_m"""

avg_ages = """with cte as (
select id, last_name_m, birth_date , gender, last_name,
	date_part('year',age(birth_date)) as age
from bpb_profile
	where living_status = 'Living'
),cte1 as (
select * from cte
where age < 100
)

select last_name_m, last_name,
coalesce(avg(case when gender = 'Male' then age end), 0) as males,
coalesce(avg(case when gender = 'Female (Daughter)' then age end), 0) daughters,
coalesce(avg(case when gender = 'Female (Daughter in Law)' then age end), 0) daughters_in_law
from cte1
group by last_name_m, last_name"""