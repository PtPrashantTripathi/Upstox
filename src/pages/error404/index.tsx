import Breadcrumb from "../../components/breadcrumb";

export default function Error404() {
    return (
        <div className="content-wrapper">
            <Breadcrumb page="home" />
            <div className="content">
                <div className="container">
                    <div className="error-page">
                        <h2 className="headline text-warning"> 404</h2>
                        <div className="error-content">
                            <h3>
                                <i className="fas fa-exclamation-triangle text-warning"></i>
                                Oops! Page not found.
                            </h3>
                            <p>
                                We could not find the page you were looking for.
                            </p>
                            <a href="./index.html">
                                you may return to dashboard
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
