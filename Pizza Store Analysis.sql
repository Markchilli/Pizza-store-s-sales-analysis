USE [Pizza Store Analysis]; 

-- Take a brief view of the dataset
SELECT TOP(10) * 
FROM pizza_sales;

SELECT DISTINCT Channel
FROM pizza_sales; 

SELECT DISTINCT OrderFrom
FROM pizza_sales;

SELECT DISTINCT province
FROM pizza_sales;

SELECT MIN(TransactionDate) AS record_start_date,
	   MAX(TransactionDate) AS record_end_date
FROM pizza_sales;

SELECT MONTH(TransactionDate) AS month_number,
	   CASE WHEN YEAR(TransactionDate) = 2021 THEN YEAR(TransactionDate)  
			WHEN YEAR(TransactionDate) = 2022 THEN YEAR(TransactionDate) ELSE '2023' END AS Year, 
	   COUNT(TransactionDate) AS number_of_order
FROM pizza_sales
GROUP BY MONTH(TransactionDate),	   
	   CASE WHEN YEAR(TransactionDate) = 2021 THEN YEAR(TransactionDate)  
			WHEN YEAR(TransactionDate) = 2022 THEN YEAR(TransactionDate) ELSE '2023' END 
ORDER BY 2 ASC, 1 ASC;

-- Before we start the analyze phase, I will clean the dataset first
-- When i use Python in Jupiter notebook for cleaning phase, I've found out that:
--1. There is no missing values, no null or NA
--2. There is no mispelled or mistyped values,
--3. There are some negative values in SalesAmount column
--4. There are outliers in SalesAmount
--5. The records in July 2023 are not as many as other periods. They don't have much in4 to produce any effective and meaningful insights.

-- Therefore, I will proceed with my analysis by dropping negative values and records in July 2023

SELECT *
INTO Pizza_sales_cleaned
FROM pizza_sales
WHERE TransactionDate < '2023-07-01' 
AND SalesAmount > 0

-- Descriptive Analytics
SELECT TOP(50) * 
FROM Pizza_sales_cleaned
;

-- Calculate total sales by month in 2022
CREATE VIEW [Monthly Sales in 2022]
AS 
SELECT CASE WHEN MONTH(TransactionDate) = 1 THEN 'Jan'
			WHEN MONTH(TransactionDate) = 2 THEN 'Feb'
			WHEN MONTH(TransactionDate) = 3 THEN 'Mar'
			WHEN MONTH(TransactionDate) = 4 THEN 'Apr'
			WHEN MONTH(TransactionDate) = 5 THEN 'May'
			WHEN MONTH(TransactionDate) = 6 THEN 'June'
			WHEN MONTH(TransactionDate) = 7 THEN 'Jul'
			WHEN MONTH(TransactionDate) = 8 THEN 'Aug'
			WHEN MONTH(TransactionDate) = 9 THEN 'Sep'
			WHEN MONTH(TransactionDate) = 10 THEN 'Oct'
			WHEN MONTH(TransactionDate) = 11 THEN 'Nov'
			ELSE 'Dec' END AS 'Month',
		ROUND(SUM(SalesAmount)/ 1000000000, 2) AS [total sales (Billion VND)]
FROM Pizza_sales_cleaned
WHERE YEAR(TransactionDate) = 2022
GROUP BY CASE WHEN MONTH(TransactionDate) = 1 THEN 'Jan'
			  WHEN MONTH(TransactionDate) = 2 THEN 'Feb'
			  WHEN MONTH(TransactionDate) = 3 THEN 'Mar'
			  WHEN MONTH(TransactionDate) = 4 THEN 'Apr'
			  WHEN MONTH(TransactionDate) = 5 THEN 'May'
			  WHEN MONTH(TransactionDate) = 6 THEN 'June'
			  WHEN MONTH(TransactionDate) = 7 THEN 'Jul'
			  WHEN MONTH(TransactionDate) = 8 THEN 'Aug'
			  WHEN MONTH(TransactionDate) = 9 THEN 'Sep'
			  WHEN MONTH(TransactionDate) = 10 THEN 'Oct'
			  WHEN MONTH(TransactionDate) = 11 THEN 'Nov'
			  ELSE 'Dec' END
;

-- Sales by month in 2022 and theirs revenue growth rate 
CREATE VIEW [Revenue summary and monthly growth rate in 2022]
AS
WITH sales_2022 AS (
	SELECT MONTH(TransactionDate) AS 'Month',
	       ROUND(SUM(SalesAmount)/ 1000000000, 2) AS [total sales (Billion VND)]
	FROM Pizza_sales_cleaned
	WHERE YEAR(TransactionDate) = 2022
	GROUP BY MONTH(TransactionDate)
)

SELECT tbl.Month,
	   tbl.[total sales (Billion VND)],
	   ROUND((tbl.[total sales (Billion VND)] - tbl.previous_month_sales) / tbl.previous_month_sales *100, 2) AS [revenue growth rate (percent)]
FROM (
	SELECT S.Month,
		   S.[total sales (Billion VND)],
		   LAG([total sales (Billion VND)], 1) OVER(ORDER BY S.Month ASC) as previous_month_sales
	FROM sales_2022 AS S
) AS tbl
;

--Calculate the monthly sales by channel in the year 2022
CREATE VIEW [Monthly Sales by channel in 2022]
AS
SELECT MONTH(TransactionDate) AS 'Month',
    SUM(CASE WHEN channel = 'Delivery' THEN SalesAmount ELSE NULL END) AS Delivery_total_sales,
    SUM(CASE WHEN channel = 'Dine In' THEN SalesAmount ELSE NULL END) AS DineIn_total_sales,
    SUM(CASE WHEN channel = 'Take Away' THEN SalesAmount ELSE NULL END) AS TakeAway_total_sales
FROM Pizza_sales_cleaned
WHERE YEAR(TransactionDate) = 2022
GROUP BY MONTH(TransactionDate)
;

--Calculate the monthly sales by order type in the year 2022
CREATE VIEW [Monthly Sales by Order type in 2022]
AS
SELECT MONTH(TransactionDate) AS 'Month',
	   SUM(CASE WHEN OrderFrom = 'WEBSITE' THEN SalesAmount ELSE NULL END) AS Website_total_sales,
       SUM(CASE WHEN OrderFrom = 'CALL CENTER' THEN SalesAmount ELSE NULL END) AS CallCenter_total_sales,
       SUM(CASE WHEN OrderFrom = 'STORE' THEN SalesAmount ELSE NULL END) AS Store_total_sales,
	   SUM(CASE WHEN OrderFrom = 'APP' THEN SalesAmount ELSE NULL END) AS App_total_sales
FROM Pizza_sales_cleaned
WHERE YEAR(TransactionDate) = 2022
GROUP BY MONTH(TransactionDate)
;

-- Calculate the monthly sales by province in the year 2022
CREATE VIEW [Monthly Sales by province in 2022]
AS
SELECT MONTH(TransactionDate) AS 'Month',
	   SUM(CASE WHEN Province = 'Hanoi' THEN SalesAmount ELSE NULL END) AS Hanoi_total_sales,
       SUM(CASE WHEN Province = 'Ho Chi Minh City' THEN SalesAmount ELSE NULL END) AS HoChiMinhcity_total_sales,
       SUM(CASE WHEN Province = 'Southern Provinces' THEN SalesAmount ELSE NULL END) AS SouthernProvinces_total_sales,
	   SUM(CASE WHEN Province = 'Nothern Provinces' THEN SalesAmount ELSE NULL END) AS NothernProvinces_total_sales
FROM Pizza_sales_cleaned
WHERE YEAR(TransactionDate) = 2022
GROUP BY MONTH(TransactionDate)
;
-- Calculate the percentage of voucher usage in 2022 by different order type
CREATE VIEW [Percentage of voucher usage by different order channel in 2022]
AS
WITH total_orders AS (
	SELECT MONTH(TransactionDate) AS 'Month',
		   CAST(SUM(CASE WHEN OrderFrom = 'WEBSITE' THEN 1 ELSE NULL END) AS FLOAT) AS Website_total_orders,
           CAST(SUM(CASE WHEN OrderFrom = 'CALL CENTER' THEN 1 ELSE NULL END) AS FLOAT) AS CallCenter_total_orders,
           CAST(SUM(CASE WHEN OrderFrom = 'STORE' THEN 1 ELSE NULL END) AS FLOAT) AS Store_total_orders,
	       CAST(SUM(CASE WHEN OrderFrom = 'APP' THEN 1 ELSE NULL END) AS FLOAT) AS App_total_orders
	FROM Pizza_sales_cleaned
	WHERE YEAR(TransactionDate) = 2022
	GROUP BY MONTH(TransactionDate)
),
voucher_used AS (
	SELECT MONTH(TransactionDate) AS 'Month',
		   SUM(CASE WHEN OrderFrom = 'WEBSITE' AND VoucherStatus = 'Yes' THEN 1 ELSE NULL END) AS Website_voucher_orders,
           SUM(CASE WHEN OrderFrom = 'CALL CENTER' AND VoucherStatus = 'Yes' THEN 1 ELSE NULL END) AS CallCenter_voucher_orders,
           SUM(CASE WHEN OrderFrom = 'STORE' AND VoucherStatus = 'Yes' THEN 1 ELSE NULL END) AS Store_voucher_orders,
	       SUM(CASE WHEN OrderFrom = 'APP' AND VoucherStatus = 'Yes' THEN 1 ELSE NULL END) AS App_voucher_orders
	FROM Pizza_sales_cleaned
	WHERE YEAR(TransactionDate) = 2022
	GROUP BY MONTH(TransactionDate)
)

SELECT t.Month,
	   ROUND(v.App_voucher_orders / t.App_total_orders * 100, 2) AS [App voucher usage (%)],
	   ROUND(v.CallCenter_voucher_orders / t.CallCenter_total_orders * 100, 2) AS [CallCenter voucher usage (%)], 
	   ROUND(v.Store_voucher_orders / t.Store_total_orders * 100, 2) AS [Store voucher usage (%)],
	   ROUND(v.Website_voucher_orders / t.Website_total_orders * 100, 2) AS [Website voucher usage (%)] 
FROM total_orders AS t JOIN voucher_used AS v
ON t.Month = v.Month

SELECT *
FROM [Percentage of voucher usage by different order channel in 2022]
ORDER BY Month ASC

-- Calculate the total sales of each day in weeks
-- Add day_name column
ALTER TABLE Pizza_sales_cleaned 
ADD [Dayname] VARCHAR(10);

UPDATE Pizza_sales_cleaned
SET [Dayname] = DATENAME(dw, TransactionDate);

CREATE VIEW [Sales by day in 2022]
AS
SELECT [Dayname],
	   ROUND(SUM(SalesAmount)/1000000000, 2) AS [total sales (Billion VND)]
FROM Pizza_sales_cleaned
WHERE YEAR(TransactionDate) = 2022
GROUP BY [Dayname]
;

-- Find top 100 valueable customers to provide them with gifts or promotion activities
CREATE VIEW [Top 100 valueable customers in 2022]
AS 
SELECT CustomerID,
	   COUNT(BillID) AS [# of orders],
	   ROUND(SUM(SalesAmount)/1000000, 2) AS [Total sales (Million VND)],
	   ROUND(AVG(SalesAmount)/ 1000, 2) AS [Average sales per order (Thousand VND)]
FROM Pizza_sales_cleaned
WHERE YEAR(TransactionDate) = 2022
GROUP BY CustomerID

SELECT TOP(100) *
FROM [Top 100 valueable customers in 2022]
ORDER BY [total sales (Million VND)] DESC

-- Calculate the customer retention rate 
-- Number of repeated customers / total customers

CREATE VIEW [Quarterly retention rate in 2022]
AS
WITH retention_customers AS (
SELECT DATEPART(QUARTER, Y1.TransactionDate) AS [Quarter],
	   COUNT(DISTINCT Y2.CustomerID) AS old_customer
FROM Pizza_sales_cleaned AS Y1
LEFT JOIN Pizza_sales_cleaned AS Y2
ON Y1.CustomerID = Y2.CustomerID AND DATEDIFF(QUARTER, Y2.TransactionDate, Y1.TransactionDate) = 1
WHERE YEAR(Y1.TransactionDate) = 2022 AND YEAR(Y2.TransactionDate) = 2022
GROUP BY DATEPART(QUARTER, Y1.TransactionDate)
)

SELECT tbl.[Quarter],
       tbl.total_customers,
	   ROUND(CAST(r.old_customer AS FLOAT)/ tbl.total_customers * 100, 2) AS customer_retention_rate 
FROM (
	SELECT DATEPART(QUARTER, P.TransactionDate) AS [Quarter],
		   COUNT(DISTINCT P.CustomerID) AS total_customers 
	FROM Pizza_sales_cleaned AS P
	WHERE YEAR( P.TransactionDate) = 2022
	GROUP BY DATEPART(QUARTER, P.TransactionDate)
) AS tbl
LEFT JOIN retention_customers AS r
ON tbl.[Quarter] = r.[Quarter];
