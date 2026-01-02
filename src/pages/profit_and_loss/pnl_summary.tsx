import RenderSummary from "../../components/render_summary";
import type { ProfitLoss } from "../../types";
import { parseNum, priceFormat } from "../../utils";

interface Props {
    data: ProfitLoss[];
}

/** Update the P&L data summary section */
const PNLSummary: React.FC<Props> = ({ data }) => {
    // Function to calculate profit/loss summary
    const investedValue = data.reduce(
        (sum, record) => sum + record.open_amount,
        0
    );
    const soldValue = data.reduce(
        (sum, record) => sum + record.close_amount,
        0
    );
    const pnlValue = data.reduce((sum, record) => sum + record.pnl_amount, 0);

    const pnlClass = pnlValue > 0 ? "bg-success" : "bg-danger";
    const pnlIcon = pnlValue > 0 ? "▲" : "▼";

    return (
        <RenderSummary
            summaryItems={[
                {
                    value: priceFormat(soldValue),
                    label: "Total Turnover",
                    colorClass: "bg-info",
                    iconClass: "fas fa-solid fa-coins",
                },
                {
                    value: priceFormat(investedValue),
                    label: "Total Invested",
                    colorClass: "bg-warning",
                    iconClass: "fas fa-piggy-bank",
                },
                {
                    value: priceFormat(pnlValue),
                    label: "Total P&L",
                    colorClass: pnlClass,
                    iconClass: "fas fa-chart-pie",
                },
                {
                    value: `${pnlIcon} ${parseNum((pnlValue * 100) / investedValue)}%`,
                    label: "Overall Return",
                    colorClass: pnlClass,
                    iconClass: "fas fa-percent",
                },
            ]}
        />
    );
};

export default PNLSummary;
