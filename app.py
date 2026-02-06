import React, { useState, useRef, useEffect } from 'react';
import Markdown from 'react-markdown';
import { AdPlatform, ValidationResult, HistoryItem } from './types';
import { PLATFORMS } from './constants';
import { checkFeasibility } from './services/geminiService';
import VerdictBadge from './components/VerdictBadge';
import HistorySidebar from './components/HistorySidebar';

const App: React.FC = () => {
  const [selectedPlatform, setSelectedPlatform] = useState<AdPlatform>(PLATFORMS[0]);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ValidationResult | null>(null);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Focus input on load
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    // Load history from local storage if needed (omitted for simplicity, but good practice)
  }, []);

  const handleCheck = async () => {
    if (!query.trim()) return;

    setLoading(true);
    setResult(null);

    try {
      const checkResult = await checkFeasibility(
        selectedPlatform.name,
        selectedPlatform.searchContext,
        query
      );

      setResult(checkResult);

      const newHistoryItem: HistoryItem = {
        id: Date.now().toString(),
        platformName: selectedPlatform.name,
        query: query,
        result: checkResult,
      };

      setHistory(prev => [newHistoryItem, ...prev]);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const loadFromHistory = (item: HistoryItem) => {
    const platform = PLATFORMS.find(p => p.name === item.platformName) || PLATFORMS[0];
    setSelectedPlatform(platform);
    setQuery(item.query);
    setResult(item.result);
  };

  return (
    <div className="flex h-screen overflow-hidden bg-slate-50">
      <HistorySidebar 
        history={history} 
        onSelect={loadFromHistory} 
        isOpen={sidebarOpen}
        toggleSidebar={() => setSidebarOpen(!sidebarOpen)}
      />

      <main className="flex-1 flex flex-col h-full overflow-hidden relative w-full">
        {/* Header */}
        <header className="bg-white border-b border-slate-200 px-6 py-4 flex items-center justify-between shrink-0 z-10">
          <div className="flex items-center gap-3">
            <button 
              onClick={() => setSidebarOpen(true)}
              className="lg:hidden text-slate-500 p-1 hover:bg-slate-100 rounded"
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
              </svg>
            </button>
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded bg-gradient-to-br from-indigo-600 to-violet-600 flex items-center justify-center text-white font-bold">
                AI
              </div>
              <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-slate-800 to-slate-600">
                AdCheck AI
              </h1>
            </div>
            <span className="hidden sm:inline-block px-2 py-1 bg-slate-100 text-xs text-slate-500 rounded border border-slate-200">
              Web広告フィジビリ確認
            </span>
          </div>
          <div className="text-xs text-slate-400 text-right">
             Powered by Gemini 2.0
          </div>
        </header>

        {/* Content Scroll Area */}
        <div className="flex-1 overflow-y-auto p-4 md:p-8">
          <div className="max-w-4xl mx-auto space-y-8">
            
            {/* Input Section */}
            <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 space-y-6">
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2">
                  1. 媒体を選択 / Select Platform
                </label>
                <div className="flex flex-wrap gap-2">
                  {PLATFORMS.map(platform => (
                    <button
                      key={platform.id}
                      onClick={() => setSelectedPlatform(platform)}
                      className={`
                        flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all
                        ${selectedPlatform.id === platform.id 
                          ? `${platform.color} text-white shadow-md shadow-slate-200 scale-105` 
                          : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50 hover:border-slate-300'}
                      `}
                    >
                      <span>{platform.icon}</span>
                      <span>{platform.name}</span>
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2">
                  2. 確認したい内容 / Verification Query
                </label>
                <div className="relative">
                  <textarea
                    ref={inputRef}
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="例：Yahooディスプレイ広告で、画像内のテキスト占有率に20%の制限はありますか？"
                    className="w-full min-h-[120px] p-4 rounded-xl border border-slate-200 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all outline-none resize-none text-slate-800 placeholder:text-slate-400"
                  />
                  <div className="absolute bottom-3 right-3">
                    <button
                      onClick={handleCheck}
                      disabled={loading || !query.trim()}
                      className={`
                        flex items-center gap-2 px-6 py-2 rounded-lg font-semibold text-white transition-all
                        ${loading || !query.trim()
                          ? 'bg-slate-300 cursor-not-allowed'
                          : 'bg-indigo-600 hover:bg-indigo-700 shadow-lg shadow-indigo-200 active:scale-95'}
                      `}
                    >
                      {loading ? (
                        <>
                          <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                          </svg>
                          <span>確認中...</span>
                        </>
                      ) : (
                        <>
                          <span>判定する</span>
                          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-5 h-5">
                            <path strokeLinecap="round" strokeLinejoin="round" d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5" />
                          </svg>
                        </>
                      )}
                    </button>
                  </div>
                </div>
                <p className="mt-2 text-xs text-slate-400">
                  ※AIは公式ヘルプページを検索し回答しますが、最終的な判断は公式ドキュメントを直接ご確認ください。
                </p>
              </div>
            </div>

            {/* Results Section */}
            {result && (
              <div className="animate-fade-in-up">
                <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
                  <div className="p-6 border-b border-slate-100 bg-slate-50/50 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                    <div className="flex items-center gap-3">
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center text-white ${selectedPlatform.color}`}>
                        {selectedPlatform.icon}
                      </div>
                      <div>
                        <div className="text-xs text-slate-500 uppercase font-bold tracking-wider">Result</div>
                        <h2 className="text-lg font-bold text-slate-800">{selectedPlatform.name}</h2>
                      </div>
                    </div>
                    <VerdictBadge verdict={result.verdict} className="text-base px-4 py-1.5" />
                  </div>

                  <div className="p-6 md:p-8">
                    <h3 className="font-semibold text-slate-900 mb-3 flex items-center gap-2">
                      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5 text-indigo-500">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
                      </svg>
                      解説サマリー
                    </h3>
                    <div className="bg-slate-50 p-6 rounded-xl border border-slate-100">
                      <article className="prose prose-slate prose-sm sm:prose-base max-w-none 
                        prose-headings:font-bold prose-headings:text-slate-800 
                        prose-p:text-slate-700 prose-p:leading-relaxed 
                        prose-strong:text-indigo-700 prose-strong:bg-indigo-50 prose-strong:px-1 prose-strong:rounded
                        prose-ul:my-2 prose-ul:list-disc prose-li:marker:text-indigo-400
                        prose-a:text-indigo-600 hover:prose-a:text-indigo-800">
                        <Markdown>{result.summary}</Markdown>
                      </article>
                    </div>

                    {result.sources.length > 0 && (
                      <div className="mt-8">
                        <h4 className="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-4 flex items-center gap-2">
                          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-4 h-4">
                            <path strokeLinecap="round" strokeLinejoin="round" d="M13.19 8.688a4.5 4.5 0 011.242 7.244l-4.5 4.5a4.5 4.5 0 01-6.364-6.364l1.757-1.757m13.35-.622l1.757-1.757a4.5 4.5 0 00-6.364-6.364l-4.5 4.5a4.5 4.5 0 001.242 7.244" />
                          </svg>
                          参照ソース (公式ヘルプ等)
                        </h4>
                        <ul className="grid gap-3 sm:grid-cols-2">
                          {result.sources.map((source, idx) => (
                            <li key={idx}>
                              <a 
                                href={source.uri}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="flex flex-col p-3 rounded-lg border border-slate-200 hover:border-indigo-400 hover:bg-indigo-50/50 hover:shadow-sm transition-all group h-full"
                              >
                                <span className="text-xs text-indigo-600 font-medium mb-1 group-hover:underline truncate w-full block">
                                  {new URL(source.uri).hostname}
                                </span>
                                <span className="text-sm font-medium text-slate-800 line-clamp-2">
                                  {source.title || 'Untitled Page'}
                                </span>
                              </a>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Empty State / Initial View */}
            {!result && !loading && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
                <div className="p-5 rounded-xl border border-slate-200 bg-white shadow-sm">
                   <div className="w-10 h-10 bg-blue-50 rounded-lg flex items-center justify-center text-blue-600 mb-3">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />
                    </svg>
                   </div>
                   <h3 className="font-semibold text-slate-900 mb-1">公式情報を検索</h3>
                   <p className="text-sm text-slate-500">最新の媒体公式ヘルプページをAIが検索・参照して回答します。</p>
                </div>
                <div className="p-5 rounded-xl border border-slate-200 bg-white shadow-sm">
                   <div className="w-10 h-10 bg-amber-50 rounded-lg flex items-center justify-center text-amber-600 mb-3">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
                    </svg>
                   </div>
                   <h3 className="font-semibold text-slate-900 mb-1">入稿規定チェック</h3>
                   <p className="text-sm text-slate-500">テキスト量、禁止ワード、画像サイズなどのルール適合性を確認。</p>
                </div>
                <div className="p-5 rounded-xl border border-slate-200 bg-white shadow-sm">
                   <div className="w-10 h-10 bg-emerald-50 rounded-lg flex items-center justify-center text-emerald-600 mb-3">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                   </div>
                   <h3 className="font-semibold text-slate-900 mb-1">明確な判定</h3>
                   <p className="text-sm text-slate-500">OK / NG / 条件付き の3段階で分かりやすく判定結果を表示。</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
      
      <style>{`
        .animate-fade-in-up {
          animation: fadeInUp 0.5s ease-out forwards;
        }
        @keyframes fadeInUp {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </div>
  );
};

export default App;
