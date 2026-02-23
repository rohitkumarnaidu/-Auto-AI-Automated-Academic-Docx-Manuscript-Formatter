export default function CategoryTabs() {
    return (
        <div className="flex flex-col items-center gap-4">
            <h2 className="text-lg font-bold text-slate-900 dark:text-white text-center">Select Category</h2>
            <div className="w-full overflow-x-auto pb-1">
                <div className="flex min-w-max bg-slate-100 dark:bg-slate-800/50 p-1.5 rounded-xl shadow-inner mx-auto">
                    <button className="px-5 sm:px-8 py-2.5 rounded-lg bg-primary text-white text-sm font-bold shadow-sm transition-all whitespace-nowrap">
                    Documents
                    </button>
                    <button className="px-5 sm:px-8 py-2.5 rounded-lg text-slate-500 dark:text-slate-400 text-sm font-medium bg-slate-200/50 dark:bg-slate-700/40 cursor-not-allowed opacity-80 flex items-center whitespace-nowrap">
                    Resume
                        <span className="text-xs bg-gray-200 dark:bg-gray-700 px-2 py-0.5 rounded ml-2">
                        Coming Soon
                        </span>
                    </button>
                    <button className="px-5 sm:px-8 py-2.5 rounded-lg text-slate-500 dark:text-slate-400 text-sm font-medium bg-slate-200/50 dark:bg-slate-700/40 cursor-not-allowed opacity-80 flex items-center whitespace-nowrap">
                    Portfolio
                        <span className="text-xs bg-gray-200 dark:bg-gray-700 px-2 py-0.5 rounded ml-2">
                        Coming Soon
                        </span>
                    </button>
                </div>
            </div>
        </div>
    );
}
