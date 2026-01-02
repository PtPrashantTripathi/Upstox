import "./css/style.css";

import Breadcrumb from "./components/breadcrumb";
import Footer from "./components/footer";
import Navigation from "./components/navigation";
import { SessionContext } from "./contexts/SessionContext";
import { useSessionState } from "./hooks/useSessionState";
import About from "./pages/about";
import CurrentHolding from "./pages/current_holding";
import Dividend from "./pages/dividend";
import Error404 from "./pages/error404";
import Home from "./pages/home";
import ProfitAndLoss from "./pages/profit_and_loss";

export default function App() {
    const session = useSessionState();

    return (
        <SessionContext value={session}>
            <Navigation
                current_user={session.data.username}
                current_page={session.data.page}
            />
            <div className="content-wrapper">
                <Breadcrumb page={session.data.page} />
                <div className="content">
                    {session.data.page === "home" ? (
                        <Home />
                    ) : session.data.page === "current_holding" ? (
                        <CurrentHolding />
                    ) : session.data.page === "profit_and_loss" ? (
                        <ProfitAndLoss />
                    ) : session.data.page === "dividend" ? (
                        <Dividend />
                    ) : session.data.page === "about" ? (
                        <About />
                    ) : (
                        <Error404 />
                    )}
                </div>
            </div>
            <Footer date={new Date(session.data.load_timestamp)} />
        </SessionContext>
    );
}
