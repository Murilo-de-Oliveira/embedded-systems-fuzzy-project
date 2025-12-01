import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Layout } from './layouts/Layout';
import Home from './pages/Home';
import Inference from './pages/Inference';
import Membership from './pages/Membership';
import Simulation from './pages/Simulation';
import MQTTMonitor from './pages/Mqtt';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/"
          element={
            <Layout>
              <Home />
            </Layout>
          }
        />
        <Route
          path="/inference"
          element={
            <Layout>
              <Inference />
            </Layout>
          }
        />
        <Route
          path="/membership"
          element={
            <Layout>
              <Membership />
            </Layout>
          }
        />
        <Route
          path="/simulation"
          element={
            <Layout>
              <Simulation />
            </Layout>
          }
        />
        <Route 
          path="/mqtt" 
          element={
            <Layout>
              <MQTTMonitor />
            </Layout>
          } 
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
