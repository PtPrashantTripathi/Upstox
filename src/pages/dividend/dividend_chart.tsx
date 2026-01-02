import type { ApexOptions } from "apexcharts";
import React from "react";
import Chart from "react-apexcharts";

import type { Dividend } from "../../types";
import { priceFormat } from "../../utils";

interface Props {
    data: Dividend[];
}

const DividendChart: React.FC<Props> = ({ data }) => {
    const grouped = Object.groupBy(data, item => item.financial_year);
    const financialYears = Object.keys(grouped).sort((a, b) =>
        a.localeCompare(b)
    );
    const dividendAmounts = financialYears.map(
        year =>
            grouped[year]?.reduce(
                (sum, item) => sum + (item.dividend_amount ?? 0),
                0
            ) ?? 0
    );

    const chartOptions: ApexOptions = {
        chart: {
            toolbar: { show: false },
        },

        xaxis: {
            categories: financialYears,
            title: {
                text: "Financial Year",
            },
            axisBorder: {
                show: false,
            },
            axisTicks: {
                show: false,
            },
        },
        yaxis: {
            labels: {
                formatter: val => priceFormat(val, false),
                style: {
                    colors: "#28a745",
                },
            },
            title: {
                text: "Dividend Amount (in ₹)",
            },
        },
        title: {
            text: "Year-wise Dividend Amount",
            align: "center",
            style: {
                fontSize: "18px",
            },
        },
        colors: ["#28a745"],
        plotOptions: {
            bar: {
                columnWidth: "50%",
                borderRadius: 4,
            },
        },
        dataLabels: {
            enabled: false,
        },
        grid: {
            borderColor: "#e0e0e0",
        },
        responsive: [
            {
                breakpoint: 768,
                options: {
                    chart: { height: 300 },
                },
            },
        ],
    };
    const chartSeries = [
        {
            name: "Dividend Amount",
            data: dividendAmounts,
        },
    ];

    return (
        <Chart
            options={chartOptions}
            series={chartSeries}
            type="bar"
            height={350}
            width="100%"
        />
    );
};

export default DividendChart;
