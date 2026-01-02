import { PageNameMapping } from "../pages";
import type { PageName } from "../types";

interface Props {
    page: PageName;
}

const Breadcrumb: React.FC<Props> = ({ page }) => {
    return (
        <div className="content-header">
            <div className="container">
                <div className="row mb-2">
                    <div className="col-sm-6">
                        <h1 className="m-0">{PageNameMapping[page]}</h1>
                    </div>
                    <div className="col-sm-6">
                        <ol className="breadcrumb float-sm-right">
                            <li className="breadcrumb-item">
                                <a href="?page=home">Home</a>
                            </li>
                            {page !== "home" && (
                                <li className="breadcrumb-item active">
                                    {PageNameMapping[page]}
                                </li>
                            )}
                        </ol>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Breadcrumb;
