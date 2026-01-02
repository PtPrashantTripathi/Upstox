import { useSessionContext } from "../../contexts/SessionContext";
import { priceFormat } from "../../utils";
import DividendChart from "./dividend_chart";
import DividendTable from "./dividend_table";

const ProfitAndLoss: React.FC = () => {
    const session = useSessionContext("dividend_data");

    if (session.data.dividend_data.length > 0) {
        return (
            <div className="container">
                <div className="row">
                    <div className="col-lg-6">
                        <div className="card">
                            <div className="card-header">
                                <h3 className="card-title">Dividend Info</h3>
                            </div>
                            <div className="card-body p-0">
                                <div className="table-responsive">
                                    <DividendTable
                                        data={session.data.dividend_data}
                                    />
                                </div>
                            </div>
                            <div className="card-footer clearfix">
                                <a className="btn btn-sm btn-secondary float-right">
                                    View All Orders
                                </a>
                            </div>
                        </div>
                    </div>

                    <div className="col-lg-6">
                        <div className="card">
                            <div className="card-header">
                                <div className="d-flex">
                                    <div className="d-flex flex-column">
                                        <h3 className="card-title">
                                            Yearly Dividend Info
                                        </h3>
                                    </div>
                                    <p className="ml-auto d-flex flex-column text-right">
                                        <span
                                            className="text-success text-bold text-lg"
                                            id="totalDividend">
                                            {priceFormat(
                                                session.data.dividend_data.reduce(
                                                    (sum, item) =>
                                                        sum +
                                                        item.dividend_amount,
                                                    0
                                                )
                                            )}
                                        </span>
                                        <span className="text-muted">
                                            Total Dividend
                                        </span>
                                    </p>
                                </div>
                            </div>
                            <div className="card-body">
                                <div className="position-relative mb-4">
                                    <DividendChart
                                        data={session.data.dividend_data}
                                    />
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }
};

export default ProfitAndLoss;
