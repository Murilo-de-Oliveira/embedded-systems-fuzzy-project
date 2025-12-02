import { Link, useLocation } from 'react-router-dom';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { useMqttStatus } from '../../hooks/useMqttStatus';

const navItems = [
  { name: 'Controle', path: '/' },
  { name: 'Pertinência', path: '/membership' },
  { name: 'Simulação', path: '/simulation' },
];

export const Topbar = () => {
  const location = useLocation();
  const { status, loading } = useMqttStatus(5000);

  const mqttStatusText = loading
    ? 'Verificando...'
    : status.connected
    ? 'Broker Online'
    : 'Desconectado';

  const mqttBadgeClass = loading
    ? 'bg-gray-400 hover:bg-gray-500'
    : status.connected
    ? 'bg-green-500 hover:bg-green-600'
    : 'bg-red-500 hover:bg-red-600';

  return (
    <div className="h-16 flex items-center justify-between px-6">
      <div className="flex items-center gap-10">
        <Link to="/" className="flex items-center space-x-2">
          <span className="inline-block font-bold text-lg whitespace-nowrap">
            Controle Fuzzy MISO
          </span>
        </Link>

        <nav className="hidden md:flex items-center space-x-6 text-sm font-medium">
          {navItems.map(item => (
            <Link
              key={item.path}
              to={item.path}
              className={`transition-colors hover:text-primary ${
                location.pathname === item.path
                  ? 'text-primary border-b-2 border-primary font-semibold'
                  : 'text-muted-foreground'
              } pb-2`}
            >
              {item.name}
            </Link>
          ))}
        </nav>
      </div>
      <div className="flex items-center space-x-4">
        <div className="hidden sm:flex items-center space-x-2">
          <span className="text-xs text-muted-foreground whitespace-nowrap">
            Status Broker:
          </span>
          <Badge variant="default" className={mqttBadgeClass}>
            {mqttStatusText}
          </Badge>
        </div>

        <Link to="/mqtt">
          <Button variant="secondary" size="sm">
            Acessar Logs de Alerta
          </Button>
        </Link>
      </div>
    </div>
  );
};
