import InteractionForm from './components/InteractionForm';
import ChatPanel from './components/ChatPanel';
import './App.css';

export default function App() {
  return (
    <div className="app-layout">
      <div className="left-panel">
        <InteractionForm />
      </div>
      <div className="right-panel">
        <ChatPanel />
      </div>
    </div>
  );
}
