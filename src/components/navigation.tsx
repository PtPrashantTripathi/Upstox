import { PageNameMapping } from "../pages";
import type { PageName } from "../types";
import { UserList, type UserName } from "../utils/usernames";

interface Props {
    current_user: UserName;
    current_page: PageName;
}
const Navigation: React.FC<Props> = ({ current_user, current_page }) => {
    return (
        <nav className="main-header navbar navbar-expand-md navbar-light">
            <div className="container">
                <a href="?page=home" className="navbar-brand">
                    <span className="brand-text">Portfolio Tracker</span>
                </a>
                <button
                    className="navbar-toggler order-1"
                    type="button"
                    data-toggle="collapse"
                    data-target="#navbarCollapse"
                    aria-controls="navbarCollapse"
                    aria-expanded="false"
                    aria-label="Toggle navigation">
                    <span className="navbar-toggler-icon"></span>
                </button>
                <div
                    className="navbar-collapse order-3 collapse"
                    id="navbarCollapse">
                    <ul className="navbar-nav">
                        {Object.entries(PageNameMapping).map(
                            ([page, label]) => (
                                <li key={page} className="nav-item">
                                    <a
                                        href={`?page=${page}`}
                                        className={`nav-link ${page === current_page ? "active" : ""}`}>
                                        {label}
                                    </a>
                                </li>
                            )
                        )}
                        <li className="nav-item dropdown">
                            <a
                                id="dropdownSubMenu1"
                                href="#"
                                data-toggle="dropdown"
                                aria-haspopup="true"
                                aria-expanded="false"
                                className="nav-link dropdown-toggle">
                                {current_user}
                            </a>
                            <ul
                                aria-labelledby="dropdownSubMenu1"
                                className="dropdown-menu border-0 shadow">
                                {UserList.filter(
                                    username => username !== current_user
                                ).map(username => (
                                    <li key={username}>
                                        <a
                                            className="dropdown-item"
                                            href={`?page=${current_page}&username=${username}`}>
                                            {username}
                                        </a>
                                    </li>
                                ))}
                            </ul>
                        </li>
                    </ul>
                </div>
            </div>
        </nav>
    );
};
export default Navigation;
