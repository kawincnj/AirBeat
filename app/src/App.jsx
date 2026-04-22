import { BrowserRouter, Routes, Route } from "react-router-dom";
import HomePage from "./pages/home";
import TrainingPage from "./pages/training";
import PluginPage from "./pages/plugin";
import BandPage from "./pages/band";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/home" element={<HomePage />} />
        <Route path="/play" element={<HomePage />} />
        <Route path="/training" element={<TrainingPage />} />
        <Route path="/plugin" element={<PluginPage />} />
        <Route path="/band" element={<BandPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;