import './App.css';
import Hero from './components/Hero';
import Intro from './components/Intro';
import TravelForm from './components/TravelForm';
import Footer from './components/Footer';

function App() {
  return (
    <div className="app">
      <Hero />
      <Intro />
      <TravelForm />
      <Footer />
    </div>
  );
}

export default App;

