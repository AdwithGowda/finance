import axios from 'axios';

const API_URL = 'https://finance-366p.onrender.com';

export const fetchExpenses = () => axios.get(`${API_URL}/expenses`);
export const createExpense = (data) => axios.post(`${API_URL}/expenses`, data);
