# Fleet maintenance tracking — requirements (synthetic example)

## Use case
One view per vehicle for the maintenance planners: current status, mileage, open faults, next service due, and cost to date.
Objective: fewer unplanned workshop visits and a monthly cost per vehicle for finance.

## Ingestion
All sources daily, batch, loaded before 07:00 so the planners see yesterday's state at the start of the shift.
High-severity faults should reach the planners within one hour (phase 2).
The company warehouse is Snowflake; Airflow is in place for scheduling.

## Epics and stories
- FLT-1 (epic) Unified vehicle view: one record per vehicle with master data, latest odometer, open faults, next service, cost to date.
- FLT-2 Daily ingestion of all four sources, finished by 07:00.
- FLT-3 Next service due: odometer against the service interval of the model.
- FLT-4 Alert the depot planner within one hour when a fault of severity "high" arrives.
- FLT-5 Monthly cost per vehicle: workshop labour + parts + fuel.
- FLT-6 Planner dashboard: fleet list with filters by depot, status and service due; vehicle detail page.
- FLT-7 Keep cost history for seven years (finance).
- FLT-8 Planners see only the vehicles of their own depot.
- FLT-9 Driver data: store only the driver id, no names (data protection).
- FLT-10 History of vehicle status changes (active, in workshop, decommissioned).
- FLT-11 (later) Predict the next unplanned fault from fault and odometer history.
- FLT-12 Data quality: an odometer reading never goes down; a reading that does is rejected and reported.

## Sources

### A. Fleet management system (FMS)
Source system: FMS, REST API (JSON), one call per depot. Identifier: `vehicle_id` (FMS key), `vin`.

| Data point | Description |
|---|---|
| vehicle_id | FMS key of the vehicle |
| vin | Vehicle identification number, 17 characters |
| plate | Registration plate |
| model | Manufacturer and model |
| depot | Home depot |
| status | active, workshop, decommissioned |
| driver_id | Current assigned driver |
| card_no | Fuel card assigned to the vehicle |

### B. Telematics provider
Source system: telematics portal, daily CSV drop on the provider's SFTP server at 04:30. Identifier: `vin`.

| Data point | Description |
|---|---|
| vin | Vehicle identification number |
| reading_date | Day of the reading |
| odometer_km | Odometer at end of day |
| engine_hours | Engine hours at end of day |
| fault_code | Manufacturer fault code, empty if none |
| fault_severity | low, medium, high |

The telematics contract keeps data for 24 months.

### C. Workshop system
Source system: workshop database (SQL, JDBC). Identifier: `work_order_id`; vehicle referenced by `plate`.

| Data point | Description |
|---|---|
| work_order_id | Work order key |
| plate | Registration plate of the vehicle |
| opened_at, closed_at | Timestamps |
| type | planned, unplanned |
| labour_hours | Hours booked |
| parts_cost, labour_cost | Cost in EUR |

### D. Fuel card provider
Monthly CSV statement sent by e-mail to finance. Identifier: `card_no`.

| Data point | Description |
|---|---|
| card_no | Fuel card number |
| txn_date | Transaction date |
| litres | Litres fuelled |
| amount | Amount in EUR |
| station | Station name |

## Consumers
- Maintenance planners: dashboard, daily.
- Depot planners: fault alerts.
- Finance: monthly cost report per vehicle.
- Later: data science, predictive service.
