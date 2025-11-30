import { InputPanel } from '@/components/common/InputPanel';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { useControlStore } from '@/store/useControlStore';

const OutputPanel = () => {
  const potenciaCRAC = useControlStore((state) => state.potenciaCRAC);

  return (
    <Card className="shadow-lg h-full">
      <CardHeader>
        <CardTitle>Potência CRAC</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-center space-y-4">
          <p className="text-2xl font-medium text-muted-foreground">Saída do Sistema Fuzzy</p>
          <h2 className="text-6xl font-extrabold text-primary">{potenciaCRAC.toFixed(1)}%</h2>
          <p className="text-sm text-muted-foreground">Potência Máxima do CRAC</p>
        </div>
      </CardContent>
    </Card>
  );
};

export default function Home() {
  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold">Painel de Controle</h1>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          <InputPanel />
        </div>
        <div className="lg:col-span-1">
          <OutputPanel />
        </div>
      </div>
    </div>
  );
}
