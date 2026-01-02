import { createContext, useContext, useEffect } from "react";
import type { SessionState } from "src/types";

// Context definition
export const SessionContext = createContext<SessionState | undefined>(
    undefined
);

// Hook for consuming session context and auto-fetching associated data
export const useSessionContext = (
    dataName:
        | "holding_trands_data"
        | "current_holding_data"
        | "dividend_data"
        | "profit_loss_data"
) => {
    const context = useContext(SessionContext);

    if (!context) {
        throw new Error(
            "useSessionContext must be used within a SessionProvider."
        );
    }
    const {
        data: { username },
        updateData,
    } = context;

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await fetch(
                    `DATA/API/${username}/${dataName}.json`
                );
                if (!response.ok) {
                    throw new Error(
                        `Failed to load ${dataName}.json: ${response.statusText}`
                    );
                }
                const json = await response.json();

                updateData({
                    [dataName]: json.data,
                    load_timestamp: new Date(json.load_timestamp),
                });
            } catch (error) {
                console.error(
                    `[SessionContext] Error loading ${dataName}.json`,
                    error
                );
            }
        };

        fetchData();
    }, [username, dataName, updateData]);

    return context;
};
