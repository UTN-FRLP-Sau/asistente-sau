from rasa.engine.graph import GraphComponent, ExecutionContext
from rasa.engine.recipes.default_recipe import DefaultV1Recipe
from rasa.engine.storage.resource import Resource
from rasa.engine.storage.storage import ModelStorage
from rasa.shared.nlu.training_data.message import Message
from rasa.shared.nlu.training_data.training_data import TrainingData
from typing import Any, Dict, List, Optional
import unicodedata
from rasa.engine.training.fingerprinting import calculate_fingerprint_key

@DefaultV1Recipe.register(
    [DefaultV1Recipe.ComponentType.MESSAGE_FEATURIZER], is_trainable=False
)
class Normalizer(GraphComponent):
    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config

    @staticmethod
    def required_components() -> List[str]:
        return []

    def process(self, messages: List[Message]) -> List[Message]:
        """Normaliza el texto de los mensajes eliminando tildes"""
        for message in messages:
            text = message.get("text")
            if text:
                normalized = unicodedata.normalize("NFKD", text).encode("ASCII", "ignore").decode("utf-8")
                message.set("text", normalized)
        return messages

    def process_training_data(self, training_data: TrainingData) -> TrainingData:
        """Procesa los datos de entrenamiento normalizando el texto"""
        self.train(training_data)
        return training_data

    def train(self, training_data: TrainingData) -> None:
        """Normaliza el texto de los ejemplos de entrenamiento eliminando tildes"""
        for example in training_data.training_examples:
            text = example.get("text")
            if text:
                normalized = unicodedata.normalize("NFKD", text).encode("ASCII", "ignore").decode("utf-8")
                example.set("text", normalized)

    @classmethod
    def create(
        cls,
        config: Dict[str, Any],
        model_storage: ModelStorage,
        resource: Resource,
        execution_context: ExecutionContext,
    ) -> "Normalizer":
        """Método de fábrica para crear una instancia del Normalizer"""
        return cls(config)

    def get_fingerprint(self) -> str:
        """Genera una huella digital basada en la configuración del componente"""
        return calculate_fingerprint_key(
            graph_component_class=self.__class__,
            config=self.config,
            inputs={},
        )