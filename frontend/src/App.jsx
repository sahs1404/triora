import { BrowserRouter, Routes, Route } from 'react-router-dom'
import NavBar from './components/NavBar.jsx'
import Dashboard from './pages/Dashboard.jsx'
import Upload from './pages/Upload.jsx'
import Simulation from './pages/Simulation.jsx'
import CVUpload from './pages/CVUpload.jsx'

function App() {
  return (
    <BrowserRouter>
      <NavBar />
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/upload" element={<Upload />} />
        <Route path="/simulate" element={<Simulation />} />
        <Route path="/cv" element={<CVUpload />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App