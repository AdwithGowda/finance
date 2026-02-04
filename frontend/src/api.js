import axios from 'axios';

const API_URL = 'https://finance-2-t4il.onrender.com';

export const fetchExpenses = () => axios.get(`${API_URL}/expenses`);
export const createExpense = (data) => axios.post(`${API_URL}/expenses`, data);
