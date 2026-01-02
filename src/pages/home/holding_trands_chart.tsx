import type { ApexOptions } from "apexcharts";
import Chart from "react-apexcharts";

import type { HoldingTrands } from "../../types";
import { priceFormat } from "../../utils";

interface Props {
    data: HoldingTrands[];
}

const HoldingTrandsChart: React.FC<Props> = ({ data }) => {
    const chartOptions: ApexOptions = {
        chart: {
            type: "area",
            toolbar: {
                show: true,
            },
            zoom: {
                enabled: true,
            },
        },
        dataLabels: {
            enabled: false,
        },
        stroke: {
            curve: "smooth",
            width: 2,
        },
        xaxis: {
            type: "datetime",
            axisBorder: {
                show: false,
            },
            axisTicks: {
                show: false,
            },
        },
        yaxis: {
            labels: {
                formatter: value => priceFormat(value, true),
                style: {
                    colors: "#8e8da4",
                },
            },
            axisBorder: {
                show: true,
            },
            axisTicks: {
                show: true,
            },
        },
        fill: {
            opacity: 0.25,
        },
        colors: ["#007bff", "#28a745"],
        tooltip: {
            x: {
                format: "yyyy-MM-dd",
            },
            y: {
                formatter: value => priceFormat(value),
            },
        },
        legend: {
            show: false,
        },
        grid: {
            show: false,
        },
    };

    const chartSeries = [
        {
            name: "Investment",
            data: data.map(d => ({
                x: new Date(d.date).getTime(),
                y: d.holding ?? 0,
            })),
        },
        {
            name: "Market Value",
            data: data.map(d => ({
                x: new Date(d.date).getTime(),
                y: d.close ?? 0,
            })),
        },
    ];

    return (
        <Chart
            options={chartOptions}
            series={chartSeries}
            type="area"
            height="100%"
            width="100%"
        />
    );
};

export default HoldingTrandsChart;
