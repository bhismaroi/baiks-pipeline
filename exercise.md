Mentoring Week 8 - Bikes Store Pipeline
Data Orchestrations - Job Preparation Program - Pacmann AI

 
source: freepik 

 
A.	Case Description
Bikes Store, a global manufacturer and retailer of bicycles, components, and accessories, aims to gain actionable insights into its operations and sales performance, Their analysis need to handle data from multiple sources such as databases, and APIs. The key challenges include:
●	Database : Transaction Database.
○	In Their Source, They have multiple schema
■	humanresources
■	person
■	production
■	purchasing
■	sales
○	ERD : img
 
○	Data : init.sql
●	API : Retrieves data external source, to get information about currency code. 
○	Represent currency information, currency code and country
○	URL : API URL
https://api-currency-azxqj1hwg-ihda-rasyadas-projects.vercel.app/api/currencydata

○	Parameters : -
○	Returned Data Type : JSON

B.	Objectives
In this exercise, there are several objectives or tasks that you need to do.
●	Project Setup
○	Setup Airflow
○	Setup Airflow Monitoring & Logging
○	Setup Data Source, Lake, and Warehouse
○	Setup Alerting
●	Create DAGs
○	Staging DAGs
○	Warehouse DAGs



 

C.	TASKS
1.	Task 1 : Project Setups (30 Points)
In this task you will setup the tools that will be used in this exercise. The details you need to setup are as follows.
a.	Airflow
In this part you need to follow the following provisions:
●	Version : 2.10.2
●	Executors : Celery Executors
●	Init Variables : airflow_variables_init.json
●	Init Connections : airflow_connections_init.yaml
●	Remote Logging : True
●	Metrics Statsd On : True

b.	Airflow Monitoring
In this part you need to setup tools to be able to monitor airflow. The components are statsd-exporter, prometheus, and grafana. Make sure all components can run properly. You can use an existing monitoring dashboards template or you can create a new one.

c.	Data Sources
In data sources, you only need to setup and initialize data in the transaction database that uses postgresql. Initialized data can be found in the following link: init.sql.

d.	Data Lake
In Data Lake, you need to run MinIO Service and initialize the bucket:
●	airflow-logs : Storing logs from Airflow
●	bikes-store : Saves csv data which is the result of extracting data sources.

e.	Data Warehouse
In the data warehouse, you need to setup postgresql and initialize the following data:
●	Staging Schema : init.sql
2.	Task 2 : Create “bikes_store_staging” DAGs (35 Points)
 

In this task you need to create a DAG that can perform the process of extracting data from the data source, saving it as a csv file in MinIO, and loading it into the “bikes_store_staging” schema in the data warehouse.
a.	Dag Details
The details of the DAG are as follows:
●	dag_id : bikes_store_staging
●	descriptions : 'Extract data and load into staging area'
●	start_date : 1 September 2024
●	schedule : daily
●	on failure callback : send alert to slack

b.	Tasks
 
The tasks you need to create in general are 3, namely "extract", "load", and "trigger_bikes_store_warehouse". The detailed explanation is as follows:
●	extract (Task Group)
 

In this task group there are 2 task groups that are run simultaneously (parallel), namely:
○	db
 

■	This Task Group is a task group to perform the process of extracting data from the transaction database. The extracted data will be saved as a csv file in MinIO (bikes-store bucket).
■	The data extraction process carried out on this task can be done incrementally (daily) or not.
■	One task in this task group represents the data extraction process on one table in the data source.
■	All tasks in this task group are run in parallel (simultaneously).
■	The operator used is the Python Operator.
■	Each task has outlets (stores information where the data is stored), for example:

  

○	api
 
■	This Task Group is a task group to perform the process of extracting data from the API. The extracted data will be saved as a csv file in MinIO (bikes-store bucket).
■	The data extraction process carried out on this task cannot be done incrementally.
■	The operator used is the Python Operator.
■	Tasks have outlets (store information where the data is stored), for example:
 

●	load
 

In this task group there are 2 task groups that are run simultaneously (parallel), namely:
○	db
 

■	This Task Group is a task group to perform the data load process from MinIO (bikes-store bucket) to the staging schema data in the warehouse.
■	The data load process carried out on this task can be done incrementally (daily) or not.
■	One task in this task group represents the data load process on one table in the staging schema.
■	All tasks in this task group are run sequentially. The order is as in the grid image above, staging.person, staging.employee, and so on.
■	The operator used is the Python Operator.
■	Each task has outlets (stores information where the data is stored), for example:

  

○	api
 
■	This Task Group is a task group to perform the process of loading data from the API that has been stored as a csv file in MinIO (bikes-store bucket) to the staging schema in the warehouse.
■	The data loading process carried out on this task cannot be done incrementally (daily).
■	The operator used is the Python Operator.
■	Tasks have outlets (store information where the data is stored), for example:

 

●	trigger_bikes_store_warehouse
○	Purpose: To trigger bikes_store_warehouse DAGs.
○	Operator : Trigger Dag Run Operator


3.	Task 3 : Create “bikes_store_warehouse” DAGs (35 Points) 

 

In this task you need to create a DAG that can perform the data transformation process from the staging schema to the warehouse schema.

a.	Dag Details
The details of the DAG are as follows:
●	dag_id : bikes_store_warehouse
●	descriptions : 'Transform data into warehouse'
●	start_date : 1 September 2024
●	schedule : None
●	on failure callback : send alert to slack

b.	Tasks
 
There are 3 tasks that you need to create in general, namely “check_is_warehouse_init”, “warehouse_init”, and “warehouse”. The detailed explanation is as follows:
●	check_is_warehouse_init
○	The purpose of this task is to determine which downstream will be run, whether “warehouse_init” or “warehouse”.
○	This is determined by the value of “BIKES_STORE_WAREHOUSE_INIT” variables. If the value is “True” then the “warehouse_init” task group will be run. But if the value is “False” then the “warehouse” task group will be run.
○	In this task you can use the task branch.

●	warehouse_init
 
○	This task will run the DBT Project using the dbt task group from the cosmos module. You can get the DBT Project through the following link.
○	Emit Dataset : True
○	Install Dependencies : True
○	Test Behavior : AFTER_ALL

●	warehouse
 
○	This task will run the DBT Project using the dbt task group from the cosmos module. You can get the DBT Project through the link provided earlier.
○	Emit Dataset : True
○	Install Dependencies : True
○	Test Behavior : AFTER_ALL
○	Exclude dim_date.







Final Output: GitHub Submission
After completing the exercise, you must upload your finished project to a GitHub repository.
Your GitHub Repository Must Contain:
1.	All project files and folders
2.	A clear and complete README.md explaining:
○	Project Overview : What this project does
○	Architecture Description : Diagram or list of components used (Airflow, PostgreSQL, MinIO, etc.)
○	How to Run and Simulate this project
○	Screenshots of Airflow UI, tasks, etc.

Validation Criteria
Your project will be considered complete if:
●	All services run smoothly
●	DAG is visible and executable in Airflow
●	In accordance with the tasks assigned to you.
○	GitHub repo is complete and well-documented



