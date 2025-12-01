import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Settings } from "lucide-react";
import { motion, AnimatePresence } from "motion/react";
import {
  Code2,
  Sparkles,
  Zap,
  ArrowRight,
  FolderOpen,
  Plus,
  X,
  Check,
  AlertCircle,
  Brain,
  Globe,
  Cpu,
} from "lucide-react";
import { useState } from "react";
import { Spinner } from "@/components/ui/spinner";
import { open as dirOpen } from "@tauri-apps/plugin-dialog";
import { open } from "@tauri-apps/plugin-shell";
import { fetch } from "@tauri-apps/plugin-http";
import { getCurrentWindow } from "@tauri-apps/api/window";
import "./App.css";

export default function UnlovableLanding() {
  const [showPopup, setShowPopup] = useState(false);
  const [showInstructions, setShowInstructions] = useState(false);
  const [projectOpenSuccess, setProjectOpenSuccess] = useState(false);
  const [openingProject, setOpeningProject] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [selectedProvider, setSelectedProvider] = useState("Ollama (local)");
  const [modelString, setModelString] = useState("");
  const [tempProvider, setTempProvider] = useState("Ollama (local)");
  const [tempModelString, setTempModelString] = useState("");
  const [error, setError] = useState("");

  // TODO: fix generation hanging the UI
  async function handleOpenButton() {
    try {
      const dir = await dirOpen({
        directory: true,
        multiple: false,
      });

      if (!dir) {
        return;
      }

      setError("");
      setOpeningProject(true);

      const response = await fetch(
        `http://localhost:8000/api/generate_project?path=${encodeURIComponent(dir)}`,
        {
          method: "POST",
        },
      );

      setOpeningProject(false);

      if (response.status === 200) {
        setProjectOpenSuccess(true);
        await new Promise((resolve) => setTimeout(resolve, 500));
        await open("http://localhost:8000/project");
        await getCurrentWindow().close();
      } else {
        setError("Failed to generate project. Please try again.");
      }
    } catch (err) {
      setOpeningProject(false);
      setError("An error occurred. Please try again.");
      console.error("Error opening project:", err);
    }
  }

  function handleNewProject() {
    setShowInstructions(true);
  }

  function closePopup() {
    setShowPopup(false);
    setShowInstructions(false);
    setProjectOpenSuccess(false);
    setError("");
  }

  // Add function to handle settings modal open
  function openSettings() {
    setTempProvider(selectedProvider);
    setTempModelString(modelString);
    setShowSettings(true);
  }

  // Add function to save settings
  function saveSettings() {
    setSelectedProvider(tempProvider);
    setModelString(tempModelString);
    setShowSettings(false);
    // TODO: Send settings to backend API
  }

  return (
    <div className="min-h-screen relative overflow-hidden bg-slate-950">
      <div className="absolute inset-0 overflow-hidden">
        <motion.div
          className="absolute inset-0 opacity-30"
          animate={{
            background: [
              "radial-gradient(circle at 20% 50%, rgba(236, 72, 153, 0.3) 0%, transparent 50%), radial-gradient(circle at 80% 50%, rgba(59, 130, 246, 0.3) 0%, transparent 50%)",
              "radial-gradient(circle at 80% 30%, rgba(236, 72, 153, 0.3) 0%, transparent 50%), radial-gradient(circle at 20% 70%, rgba(59, 130, 246, 0.3) 0%, transparent 50%)",
              "radial-gradient(circle at 50% 80%, rgba(236, 72, 153, 0.3) 0%, transparent 50%), radial-gradient(circle at 50% 20%, rgba(59, 130, 246, 0.3) 0%, transparent 50%)",
              "radial-gradient(circle at 20% 50%, rgba(236, 72, 153, 0.3) 0%, transparent 50%), radial-gradient(circle at 80% 50%, rgba(59, 130, 246, 0.3) 0%, transparent 50%)",
            ],
          }}
          transition={{
            duration: 10,
            repeat: Infinity,
            ease: "linear",
          }}
        />
      </div>
      <div className="relative z-10">
        <nav className="px-6 py-6">
          <div className="max-w-7xl mx-auto flex items-center justify-between">
            <motion.div
              className="flex items-center gap-3"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6 }}
            >
              <span className="text-4xl">💔</span>
              <span className="text-2xl font-bold text-white font-sans">
                unlovable
              </span>
            </motion.div>

            <motion.button
              onClick={openSettings}
              className="flex items-center gap-3 px-4 py-2 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 transition-all"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6 }}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <Settings size={18} className="text-slate-400" />
              <div className="flex flex-col items-start">
                <span className="text-xs text-slate-400 font-sans">
                  {selectedProvider}
                </span>
                {modelString && (
                  <span className="text-xs text-slate-500 font-mono">
                    {modelString}
                  </span>
                )}
              </div>
            </motion.button>
          </div>
        </nav>

        <div className="max-w-6xl mx-auto px-6 pt-20 pb-32 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
          >
            <h1 className="text-6xl md:text-7xl font-bold text-white mb-6 leading-tight font-sans">
              Build multi-page apps
              <br />
              <span className="bg-linear-to-r from-pink-400 to-blue-400 bg-clip-text text-transparent">
                with plain text
              </span>
            </h1>
          </motion.div>

          <motion.p
            className="text-xl text-slate-300 mb-12 max-w-2xl mx-auto font-sans"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
          >
            No frameworks. No build steps. No complexity. Just describe what you
            want, and unlovable creates beautiful, functional applications
            instantly.
          </motion.p>

          <motion.div
            className="flex flex-col sm:flex-row gap-4 justify-center items-center"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.6 }}
          >
            <button
              onClick={() => setShowPopup(true)}
              className="group flex items-center gap-2 px-8 py-4 rounded-xl bg-linear-to-r from-pink-500 to-blue-500 text-white font-semibold hover:shadow-2xl hover:shadow-pink-500/50 transition-all"
            >
              Get Started
              <ArrowRight
                size={20}
                className="group-hover:translate-x-1 transition-transform"
              />
            </button>
            <button className="px-8 py-4 rounded-xl bg-white/10 backdrop-blur-md border border-white/20 text-white font-semibold hover:bg-white/20 transition-all">
              Learn More
            </button>
          </motion.div>
        </div>
        <div className="max-w-6xl mx-auto px-6 pb-32">
          <div className="grid md:grid-cols-3 gap-6">
            {[
              {
                icon: Code2,
                title: "Plain Text Input",
                description:
                  "Describe your app in natural language. No code required, no learning curve.",
                delay: 0.2,
              },
              {
                icon: Zap,
                title: "Instant Generation",
                description:
                  "Watch your ideas transform into working applications in seconds, not hours.",
                delay: 0.4,
              },
              {
                icon: Sparkles,
                title: "Multi-Page Magic",
                description:
                  "Create complex, multi-page experiences with routing, state, and navigation.",
                delay: 0.6,
              },
            ].map((feature, i) => (
              <motion.div
                key={i}
                className="p-8 rounded-2xl bg-white/5 backdrop-blur-md border border-white/10 hover:bg-white/10 transition-all"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: feature.delay }}
              >
                <div className="w-12 h-12 rounded-lg bg-linear-to-r from-pink-500 to-blue-500 flex items-center justify-center mb-4">
                  <feature.icon className="text-white" size={24} />
                </div>
                <h3 className="text-xl font-semibold text-white mb-3 font-sans">
                  {feature.title}
                </h3>
                <p className="text-slate-400 font-sans">
                  {feature.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
        <div className="max-w-4xl mx-auto px-6 pb-32">
          <motion.div
            className="rounded-2xl bg-white/5 backdrop-blur-md border border-white/10 overflow-hidden"
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
          >
            <div className="bg-white/5 px-6 py-4 border-b border-white/10 flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-red-500"></div>
              <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
              <div className="w-3 h-3 rounded-full bg-green-500"></div>
              <span className="ml-4 text-slate-400 text-sm font-mono">
                unlovable.txt
              </span>
            </div>
            <div className="p-8 font-mono text-sm text-slate-300 leading-relaxed">
              <div className="text-pink-400 font-mono">
                Create a simple blog app with:
              </div>
              <div className="ml-4 mt-2 font-mono">
                - A home page listing all posts
              </div>
              <div className="ml-4 font-mono">- Individual post pages</div>
              <div className="ml-4 font-mono">- A contact form</div>
              <div className="ml-4 font-mono">- Dark mode toggle</div>
              <div className="mt-4 text-blue-400 font-mono">
                → Done. Your app is ready.
              </div>
            </div>
          </motion.div>
        </div>
        <footer className="border-t border-white/10 bg-white/5 backdrop-blur-md">
          <div className="max-w-6xl mx-auto px-6 py-8 flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="flex items-center gap-3">
              <span className="text-2xl">💔</span>
              <span className="text-slate-400">
                Built with heartbreak and AI
              </span>
            </div>
          </div>
        </footer>
      </div>
      <AnimatePresence>
        {showPopup && (
          <motion.div
            className="fixed inset-0 z-50 flex items-center justify-center p-4"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <motion.div
              className="absolute inset-0 bg-black/60 backdrop-blur-sm"
              onClick={closePopup}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            />

            <motion.div
              className="relative w-full max-w-md rounded-2xl bg-slate-900/95 backdrop-blur-xl border border-white/20 shadow-2xl"
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              transition={{ type: "spring", duration: 0.5 }}
            >
              <button
                onClick={closePopup}
                className="absolute top-4 right-4 p-2 rounded-lg hover:bg-white/10 transition-colors"
              >
                <X size={20} className="text-slate-400" />
              </button>

              <div className="p-8">
                <AnimatePresence mode="wait">
                  {!showInstructions ? (
                    <motion.div
                      key="options"
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: -20 }}
                      transition={{ duration: 0.3 }}
                    >
                      <h2 className="text-2xl font-bold text-white mb-2 font-sans">
                        Get Started
                      </h2>
                      <p className="text-slate-400 mb-8 font-sans">
                        Choose how you'd like to begin
                      </p>

                      {error && (
                        <motion.div
                          className="mb-4 p-4 rounded-lg bg-red-500/10 border border-red-500/30 flex items-start gap-3"
                          initial={{ opacity: 0, y: -10 }}
                          animate={{ opacity: 1, y: 0 }}
                        >
                          <AlertCircle
                            size={20}
                            className="text-red-400 shrink-0 mt-0.5"
                          />
                          <p className="text-red-400 text-sm font-sans">
                            {error}
                          </p>
                        </motion.div>
                      )}

                      <div className="space-y-3">
                        <button
                          onClick={handleOpenButton}
                          disabled={openingProject}
                          className={`w-full flex items-center gap-4 p-6 rounded-xl border transition-all group ${
                            openingProject
                              ? "bg-linear-to-r from-blue-500/20 to-cyan-500/20 border-blue-400/50 cursor-wait"
                              : projectOpenSuccess
                                ? "bg-linear-to-r from-green-500/20 to-emerald-500/20 border-green-400/50"
                                : "bg-white/5 border-white/10 hover:bg-white/10 hover:border-white/20"
                          }`}
                        >
                          {!openingProject && !projectOpenSuccess && (
                            <>
                              <div className="w-12 h-12 rounded-lg bg-linear-to-r from-blue-500 to-cyan-500 flex items-center justify-center shrink-0">
                                <FolderOpen size={24} className="text-white" />
                              </div>
                              <div className="text-left">
                                <h3 className="text-lg font-semibold text-white group-hover:text-blue-400 transition-colors font-sans">
                                  Open Project
                                </h3>
                              </div>
                            </>
                          )}
                          {openingProject && (
                            <>
                              <div className="w-12 h-12 rounded-lg bg-linear-to-r from-blue-500 to-cyan-500 flex items-center justify-center shrink-0">
                                <Spinner />
                              </div>
                              <div className="text-left">
                                <h3 className="text-lg font-semibold text-white transition-colors font-sans">
                                  Generating Project...
                                </h3>
                                <p className="text-sm text-slate-400 font-sans">
                                  This may take a moment
                                </p>
                              </div>
                            </>
                          )}
                          {projectOpenSuccess && (
                            <>
                              <div className="w-12 h-12 rounded-lg bg-linear-to-r from-green-500 to-emerald-500 flex items-center justify-center shrink-0">
                                <Check size={24} className="text-white" />
                              </div>
                              <div className="text-left">
                                <h3 className="text-lg font-semibold text-green-400 transition-colors font-sans">
                                  Generation Successful
                                </h3>
                              </div>
                            </>
                          )}
                        </button>
                        <button
                          onClick={handleNewProject}
                          disabled={openingProject}
                          className="w-full flex items-center gap-4 p-6 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 hover:border-white/20 transition-all group disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          <div className="w-12 h-12 rounded-lg bg-linear-to-r from-pink-500 to-purple-500 flex items-center justify-center shrink-0">
                            <Plus size={24} className="text-white" />
                          </div>
                          <div className="text-left">
                            <h3 className="text-lg font-semibold text-white group-hover:text-pink-400 transition-colors font-sans">
                              New Project
                            </h3>
                            <p className="text-sm text-slate-400 font-sans">
                              Start a fresh project from scratch
                            </p>
                          </div>
                        </button>
                      </div>
                    </motion.div>
                  ) : (
                    <motion.div
                      key="instructions"
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: 20 }}
                      transition={{ duration: 0.3 }}
                    >
                      <h2 className="text-2xl font-bold text-white mb-2 font-sans">
                        Create New Project
                      </h2>
                      <p className="text-slate-400 mb-6 font-sans">
                        Follow these steps to get started
                      </p>

                      <div className="space-y-4 mb-6">
                        {[
                          {
                            step: 1,
                            title: "Create a new folder",
                            description:
                              "Choose a location for your project files",
                            delay: 0.1,
                          },
                          {
                            step: 2,
                            title: "Create an index.txt file",
                            description: "Describe your app in plain text",
                            delay: 0.2,
                          },
                          {
                            step: 3,
                            title: "Define routes",
                            description:
                              "Create folders with index.txts to define routes (i.e., <url>/home, <url>/about)",
                            delay: 0.3,
                          },
                          {
                            step: 4,
                            title: "Run unlovable",
                            description:
                              "Open your folder as a project in unlovable and watch your app come to life",
                            delay: 0.4,
                          },
                        ].map((item) => (
                          <motion.div
                            key={item.step}
                            className="p-4 rounded-lg bg-white/5 border border-white/10"
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.3, delay: item.delay }}
                          >
                            <div className="flex items-start gap-3">
                              <span className="shrink-0 w-6 h-6 rounded-full bg-pink-500 flex items-center justify-center text-white text-sm font-bold">
                                {item.step}
                              </span>
                              <div>
                                <h4 className="text-white font-semibold mb-1 font-sans">
                                  {item.title}
                                </h4>
                                <p className="text-sm text-slate-400 font-sans">
                                  {item.description}
                                </p>
                              </div>
                            </div>
                          </motion.div>
                        ))}
                      </div>

                      <motion.button
                        onClick={() => setShowInstructions(false)}
                        className="w-full py-3 rounded-lg bg-linear-to-r from-pink-500 to-purple-500 text-white font-semibold hover:shadow-xl hover:shadow-pink-500/50 transition-all font-sans"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ duration: 0.3, delay: 0.4 }}
                      >
                        Got it!
                      </motion.button>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
      // Update the Dialog content with proper theming and animations
      <Dialog open={showSettings} onOpenChange={setShowSettings}>
        <DialogContent className="bg-slate-900/95 backdrop-blur-xl border-white/20 text-white max-w-md">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            <DialogHeader>
              <DialogTitle className="text-2xl font-bold font-sans flex items-center gap-2">
                <Settings size={24} className="text-pink-400" />
                Settings
              </DialogTitle>
              <DialogDescription className="text-slate-400 font-sans">
                Configure your model provider and settings
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-6 py-6">
              <motion.div
                className="space-y-3"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: 0.1 }}
              >
                <Label
                  htmlFor="provider"
                  className="text-white font-sans text-sm font-medium"
                >
                  Model Provider
                </Label>
                <Select value={tempProvider} onValueChange={setTempProvider}>
                  <SelectTrigger className="bg-white/5 border-white/10 text-white hover:bg-white/10 transition-all h-12">
                    <SelectValue placeholder="Select provider" />
                  </SelectTrigger>
                  <SelectContent className="bg-slate-900 border-white/20">
                    <SelectItem
                      value="Ollama (local)"
                      className="text-white hover:bg-white/10 cursor-pointer"
                    >
                      <div className="flex items-center gap-2">
                        <Cpu size={16} className="text-slate-400" />
                        <span>Ollama (local)</span>
                      </div>
                    </SelectItem>
                    <SelectItem
                      value="Google"
                      className="text-white hover:bg-white/10 cursor-pointer"
                    >
                      <div className="flex items-center gap-2">
                        <Globe size={16} className="text-slate-400" />
                        <span>Google</span>
                      </div>
                    </SelectItem>
                    <SelectItem
                      value="Groq"
                      className="text-white hover:bg-white/10 cursor-pointer"
                    >
                      <div className="flex items-center gap-2">
                        <Zap size={16} className="text-slate-400" />
                        <span>Groq</span>
                      </div>
                    </SelectItem>
                    <SelectItem
                      value="OpenAI"
                      className="text-white hover:bg-white/10 cursor-pointer"
                    >
                      <div className="flex items-center gap-2">
                        <Brain size={16} className="text-slate-400" />
                        <span>OpenAI</span>
                      </div>
                    </SelectItem>
                  </SelectContent>
                </Select>
              </motion.div>

              <motion.div
                className="space-y-3"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: 0.2 }}
              >
                <Label
                  htmlFor="model-string"
                  className="text-white font-sans text-sm font-medium"
                >
                  Model String
                </Label>
                <Input
                  id="model-string"
                  value={tempModelString}
                  onChange={(e) => setTempModelString(e.target.value)}
                  placeholder="e.g., gpt-4, llama3, gemini-pro"
                  className="bg-white/5 border-white/10 text-white placeholder:text-slate-500 focus:border-pink-400/50 focus:ring-2 focus:ring-pink-400/20 transition-all h-12 font-mono"
                />
              </motion.div>

              <motion.div
                className="flex gap-3 pt-2"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: 0.3 }}
              >
                <motion.button
                  onClick={() => setShowSettings(false)}
                  className="flex-1 py-3 px-4 rounded-lg bg-white/5 border border-white/10 text-white font-semibold hover:bg-white/10 transition-all font-sans"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  Cancel
                </motion.button>
                <motion.button
                  onClick={saveSettings}
                  className="flex-1 py-3 px-4 rounded-lg bg-gradient-to-r from-pink-500 to-blue-500 text-white font-semibold hover:shadow-xl hover:shadow-pink-500/50 transition-all font-sans"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  Save
                </motion.button>
              </motion.div>
            </div>
          </motion.div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
