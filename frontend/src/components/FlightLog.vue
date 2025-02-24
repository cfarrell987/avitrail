<script setup lang="ts">
import { ref, watch } from "vue";
import axios from "axios";

interface Flight {
  id: number;
  flight_number: string;
  departure_airport: string;
  arrival_airport: string;
}

const flights = ref<Flight[]>([]);
const token = ref<string>("");
const loading = ref<boolean>(false);
const username = ref<string>("");
const password = ref<string>("");

watch(token, (newToken) => {
  if (newToken) {
    fetchFlights();
  }
});

const fetchFlights = async () => {
  loading.value = true;
  try {
    const response = await axios.get("http://localhost:8000/api/flights/", {
      headers: { Authorization: `Token ${token.value}` },
    });
    flights.value = response.data;
  } catch (error) {
    console.error("Error fetching flights", error);
  }
  loading.value = false;
};

const handleLogin = async (): Promise<void> => {
  try {
    const response = await axios.post("http://localhost:8000/api/auth/", {
      username: username.value,
      password: password.value,
    });
    token.value = response.data.token;
  } catch (error) {
    console.error("Login failed", error);
  }
};
</script>

<template>
  <div>
    <div v-if="!token">
      <p>Login to view your flights</p>
      <form @submit.prevent="handleLogin">
        <label for="username">Username:</label>
        <input type="text" id="username" v-model="username" required />

        <label for="password">Password:</label>
        <input type="password" id="password" v-model="password" required />

        <button type="submit">Login</button>
      </form>
    </div>
    <div v-else>
      <h2 class="text-lg font-semibold">Your Flights</h2>
      <p v-if="loading">Loading...</p>
      <ul v-else>
        <li v-for="flight in flights" :key="flight.id">
          {{ flight.flight_number }} - {{ flight.departure_airport }} to {{ flight.arrival_airport }}
        </li>
      </ul>
    </div>
  </div>
</template>


<style scoped>
button {
  background-color: #007bff;
  color: white;
  padding: 8px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
button:hover {
  background-color: #0056b3;
}
input {
  display: block;
  margin-bottom: 10px;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
}
</style>
