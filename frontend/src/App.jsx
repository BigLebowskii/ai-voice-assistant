import { useState } from "react";

import "./App.css";
import LiveKitModal from "./components/LiveKitModal";

function App() {
  const [showSupport, setShowSupport] = useState(false);
  const handleSupportClick = () => {
    setShowSupport(true);
  };
  return (
    <div className="app">
      <header className>
        <div className="logo">Necrosis.ai</div>
      </header>

      <main>
        <section className="hero">
          <h1>Your own Personalized Voice Assistant!</h1>
          <p>
            Apply to our newsletter and receive updates about our latest
            products.
          </p>
          <div className="search-bar">
            <input type="text" placeholder="Enter your E-Mail address"></input>
          </div>
        </section>

        <button className="support-button" onClick={handleSupportClick}>
          Talk to the Assistant!
        </button>
      </main>

      {showSupport && <LiveKitModal setShowSupport={setShowSupport} />}
    </div>
  );
}

export default App;
