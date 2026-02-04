import axios from "axios";

const API = axios.create({
  baseURL: "https://finance-lz2e.onrender.com",
  headers: {
    "Content-Type": "application/json",
  },
});

// GET expenses
export const getExpenses = async () => {
  const res = await API.get("/expenses");
  return res.data;
};

// ADD expense
export const addExpense = async (expense) => {
  return await API.post("/expenses", expense);
};

// DELETE expense
export const deleteExpense = async (id) => {
  return await API.delete(`/expenses/${id}`);
};
