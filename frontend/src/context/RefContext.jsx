import { createContext, useContext, useState, useEffect, useCallback } from "react";
import { getVenues } from "../api/venuesApi";
import { getCategories } from "../api/categoriesApi";

const RefContext = createContext();

export function RefProvider({ children }) {
  const [venues, setVenues] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchRefData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [venuesData, categoriesData] = await Promise.all([
        getVenues(),
        getCategories()
      ]);
      setVenues(venuesData || []);
      setCategories(categoriesData || []);
    } catch (err) {
      console.error("Failed to load reference data:", err);
      setError(err.message || "Failed to load reference data.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchRefData();
  }, [fetchRefData]);

  const value = {
    venues,
    categories,
    loading,
    error,
    refreshRefs: fetchRefData
  };

  return <RefContext.Provider value={value}>{children}</RefContext.Provider>;
}

export function useRefData() {
  const context = useContext(RefContext);
  if (!context) {
    throw new Error("useRefData must be used within a RefProvider");
  }
  return context;
}
