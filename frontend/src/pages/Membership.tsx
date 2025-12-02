import { useControlStore } from '@/store/useControlStore';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';

export default function Membership() {
  const plots = useControlStore((s) => s.plots);

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Processo de Pertinência Fuzzy</h1>

      {!plots ? (
        <div className="text-muted-foreground text-lg">
          Nenhum cálculo fuzzy foi executado ainda. Vá para <b>"Painel de Entradas"</b> e execute um
          cálculo manual.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Pertinência — Erro</CardTitle>
            </CardHeader>
            <CardContent>
              <img
                src={`data:image/png;base64,${plots.erro}`}
                alt="Pertinência do erro"
                className="rounded border"
              />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Pertinência — Delta Erro</CardTitle>
            </CardHeader>
            <CardContent>
              <img
                src={`data:image/png;base64,${plots.delta}`}
                alt="Pertinência delta erro"
                className="rounded border"
              />
            </CardContent>
          </Card>

          {/* TEMP EXTERNA */}
          <Card>
            <CardHeader>
              <CardTitle>Pertinência — Temp. Externa</CardTitle>
            </CardHeader>
            <CardContent>
              <img
                src={`data:image/png;base64,${plots.temp}`}
                alt="Pertinência temp externa"
                className="rounded border"
              />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Pertinência — Carga Térmica</CardTitle>
            </CardHeader>
            <CardContent>
              <img
                src={`data:image/png;base64,${plots.carga}`}
                alt="Pertinência carga térmica"
                className="rounded border"
              />
            </CardContent>
          </Card>

          <Card className="md:col-span-2">
            <CardHeader>
              <CardTitle>Saída — P_CRAC</CardTitle>
            </CardHeader>
            <CardContent>
              <img
                src={`data:image/png;base64,${plots.pcrac}`}
                alt="pcrac plot"
                className="rounded border"
              />
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
