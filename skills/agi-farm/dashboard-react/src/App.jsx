import { useState } from 'react';
import { useDashboard } from './hooks/useDashboard';
import Header   from './components/Header';
import Nav      from './components/Nav';
import Overview  from './components/tabs/Overview';
import Agents    from './components/tabs/Agents';
import Tasks     from './components/tabs/Tasks';
import Projects  from './components/tabs/Projects';
import Velocity  from './components/tabs/Velocity';
import Budget    from './components/tabs/Budget';
import OKRs      from './components/tabs/OKRs';
import RD        from './components/tabs/RD';
import Broadcast from './components/tabs/Broadcast';
import Crons     from './components/tabs/Crons';
import HITLTab   from './components/tabs/HITL';
import Knowledge from './components/tabs/Knowledge';
import Comms     from './components/tabs/Comms';
import AlertsTab from './components/tabs/Alerts';

const TABS = [
  'Overview','Agents','Tasks','Projects',
  'Crons','HITL','Alerts',
  'Velocity','Budget','OKRs',
  'Knowledge','Comms',
  'R&D','Broadcast',
];

function Connecting() {
  return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center',
      height:'calc(100vh - 100px)', gap:16 }}>
      <span style={{ fontSize:32 }}>🦅</span>
      <div style={{ color:'var(--cyan)', fontSize:14, fontWeight:600 }}>Connecting to Ops Room…</div>
      <div style={{ color:'var(--muted)', fontSize:11 }}>Waiting for SSE push from dashboard.py</div>
    </div>
  );
}

export default function App() {
  const [activeTab, setActiveTab] = useState('Overview');
  const { data, connected, lastUpdated, updateCount } = useDashboard();

  const tabProps = { data, lastUpdated };

  // Badge counts for nav tabs
  const badges = data ? {
    'HITL':   (data.hitl_tasks  || []).length,
    'Alerts': (data.alerts      || []).length,
    'Crons':  (data.crons || []).filter(j => (j._consecutive_errors || 0) >= 3).length,
  } : {};

  const renderTab = () => {
    if (!data) return <Connecting />;
    switch (activeTab) {
      case 'Overview':  return <Overview  {...tabProps} />;
      case 'Agents':    return <Agents    {...tabProps} />;
      case 'Tasks':     return <Tasks     {...tabProps} />;
      case 'Projects':  return <Projects  {...tabProps} />;
      case 'Velocity':  return <Velocity  {...tabProps} />;
      case 'Budget':    return <Budget    {...tabProps} />;
      case 'OKRs':      return <OKRs      {...tabProps} />;
      case 'R&D':       return <RD        {...tabProps} />;
      case 'Broadcast': return <Broadcast {...tabProps} />;
      case 'Crons':     return <Crons     {...tabProps} />;
      case 'HITL':      return <HITLTab   {...tabProps} />;
      case 'Knowledge': return <Knowledge {...tabProps} />;
      case 'Comms':     return <Comms     {...tabProps} />;
      case 'Alerts':    return <AlertsTab {...tabProps} />;
      default:          return <Overview  {...tabProps} />;
    }
  };

  return (
    <div style={{ minHeight:'100vh' }}>
      <Header data={data} connected={connected} lastUpdated={lastUpdated} updateCount={updateCount} />
      <Nav tabs={TABS} active={activeTab} onChange={setActiveTab} badges={badges} />
      <main style={{ padding:16 }}>
        {renderTab()}
      </main>
    </div>
  );
}
