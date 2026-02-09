import { useState, useEffect } from 'react';
import { supabase } from '../lib/supabaseClient';

export default function TreinoApp() {
  const [exercicios, setExercicios] = useState([]);
  const [historico, setHistorico] = useState({});

  // 1. Carregar exercícios e o ÚLTIMO registro de cada um
  useEffect(() => {
    async function fetchData() {
      const { data: exData } = await supabase.from('exercicios').select('*');
      setExercicios(exData);

      // Para cada exercício, busca a carga mais recente
      exData.forEach(async (ex) => {
        const { data: lastLog } = await supabase
          .from('logs_treino')
          .select('carga, reps')
          .eq('exercicio_id', ex.id)
          .order('data', { ascending: false })
          .limit(1);
        
        if (lastLog?.[0]) {
          setHistorico(prev => ({ ...prev, [ex.id]: lastLog[0] }));
        }
      });
    }
    fetchData();
  }, []);

  // 2. Função para salvar o treino do dia
  const salvarSerie = async (id, carga, reps) => {
    const { error } = await supabase
      .from('logs_treino')
      .insert([{ exercicio_id: id, carga: parseFloat(carga), reps: parseInt(reps) }]);
    
    if (!error) alert("Carga registrada!");
  };

  return (
    <div className="max-w-md mx-auto p-4 bg-slate-50 min-h-screen">
      <h1 className="text-2xl font-bold mb-6 text-slate-800">Meu Treino 💪</h1>
      
      {exercicios.map(ex => (
        <div key={ex.id} className="bg-white p-4 rounded-2xl shadow-sm mb-4 border border-slate-200">
          <div className="flex justify-between items-start mb-2">
            <div>
              <h3 className="font-bold text-lg text-slate-700">{ex.nome}</h3>
              <span className="text-xs font-medium bg-slate-100 px-2 py-1 rounded text-slate-500 uppercase">
                {ex.musculo}
              </span>
            </div>
            
            {/* VALOR DA ÚLTIMA SEMANA (Igual sua planilha) */}
            {historico[ex.id] && (
              <div className="text-right text-orange-600 bg-orange-50 p-2 rounded-lg border border-orange-100">
                <p className="text-[10px] uppercase font-bold">Anterior</p>
                <p className="text-sm font-bold">{historico[ex.id].carga}kg x {historico[ex.id].reps}</p>
              </div>
            )}
          </div>

          <div className="flex gap-2 mt-4">
            <input 
              id={`c-${ex.id}`} type="number" placeholder="Kg" 
              className="w-full p-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-blue-500 outline-none"
            />
            <input 
              id={`r-${ex.id}`} type="number" placeholder="Reps" 
              className="w-full p-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-blue-500 outline-none"
            />
            <button 
              onClick={() => {
                const c = document.getElementById(`c-${ex.id}`).value;
                const r = document.getElementById(`r-${ex.id}`).value;
                salvarSerie(ex.id, c, r);
              }}
              className="bg-blue-600 text-white px-6 rounded-xl font-bold active:scale-95 transition-transform"
            >
              ✓
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
