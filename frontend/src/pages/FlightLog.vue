<script setup lang="ts">
import { ref, watch, onMounted } from "vue";
import axios from "axios";
import type { components } from "../schema";

type Flight = components["schemas"]["Flight"];
type Airport = components["schemas"]["Airport"];
type Airline = components["schemas"]["Airline"];

const flights = ref<Flight[]>([]);
const airports = ref<Airport[]>([]);
const airlines = ref<Airline[]>([]);
const token = ref<string>(localStorage.getItem("token") || "");
const loading = ref<boolean>(false);
const username = ref<string>("");
const password = ref<string>("");

watch(token, (newToken) => {
  if (newToken) {
    localStorage.setItem("token", newToken);
    fetchFlights();
    fetchAirports();
    fetchAirlines();
  } else {
    localStorage.removeItem("token");
  }
});

const fetchFlights = async () => {
  loading.value = true;
  try {
    const response = await axios.get("http://localhost:8000/api/flights/flights/", {
      headers: { Authorization: `Token ${token.value}` },
    });
    flights.value = response.data;
  } catch (error) {
    console.error("Error fetching flights", error);
  }
  loading.value = false;
};

const fetchAirports = async () => {
  try {
    const response = await axios.get("http://localhost:8000/api/flights/airports/");
    console.log(response.data);
  } catch (error) {
    console.error("Error fetching airports", error);
  }
};

const fetchAirlines = async () => {
  try {
    const response = await axios.get("http://localhost:8000/api/flights/airlines/");
    console.log(response.data);
  } catch (error) {
    console.error("Error fetching airlines", error);
  }
};


const handleLogin = async () => {
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

onMounted(() => {
  if (token.value) {
    fetchFlights();
    fetchAirlines()
    fetchAirports()
  }
});

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
      <table>
      <thead>
                <tr>
                  <th>Flight Number</th>
                  <th>Departure Airport</th>
                  <th>Arrival Airport</th>
                  <th>Departure Time</th>
                  <th>Arrival Time</th>
                  <th>Duration</th>
                  <th>Airline</th>
                  <th>Aircraft</th>
                  <th>Distance</th>
                  <th>Tail Number</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="flight in flights" :key="flight.id">
                  <td>{{ flight.flight_number }}</td>
                  <td>{{ flight.departure_airport }}</td>
                  <td>{{ flight.arrival_airport }}</td>
                  <td>{{ flight.departure_time }}</td>
                  <td>{{ flight.arrival_time }}</td>
                  <td>{{ flight.duration }}</td>
                  <td>{{ flight.airline }}</td>
                  <td>{{ flight.aircraft }}</td>
                  <td>{{ flight.distance }}</td>
                  <td>{{ flight.tail_number }}</td>
                </tr>
              </tbody>
    </table>
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
table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}
</style>
