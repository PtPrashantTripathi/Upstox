import { useSessionContext } from "../../contexts/SessionContext";
import FinancialSummary from "./financial_summary";
import HoldingTrandsChart from "./holding_trands_chart";

const Home: React.FC = () => {
    const session = useSessionContext("holding_trands_data");

    if (session.data.holding_trands_data.length > 0) {
        return (
            <div className="container">
                <div className="row">
                    <FinancialSummary data={session.data.holding_trands_data} />
                </div>
                <div className="row">
                    <div className="col">
                        <div className="card">
                            <div className="card-header">
                                <div className="d-flex justify-content-between">
                                    <h3 className="card-title">
                                        Portfolio Performance
                                    </h3>
                                    <a>View Report</a>
                                </div>
                            </div>
                            <div className="card-body">
                                <div className="position-relative mb-4">
                                    <div
                                        className="chart"
                                        style={{
                                            height: "20rem",
                                        }}>
                                        <HoldingTrandsChart
                                            data={
                                                session.data.holding_trands_data
                                            }
                                        />
                                    </div>
                                </div>
                                <div className="d-flex flex-row justify-content-end">
                                    <span className="mr-2">
                                        <i className="fas fa-square text-primary"></i>
                                        Investment
                                    </span>
                                    <span>
                                        <i className="fas fa-square text-success"></i>
                                        Market Value
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }
};

export default Home;
