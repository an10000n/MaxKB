# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： tokenizer_manage_config.py
    @date：2024/4/28 10:17
    @desc:
"""
class TokenizerManage:
    tokenizer = None

    @staticmethod
    def get_tokenizer():
        from transformers import GPT2TokenizerFast
        if TokenizerManage.tokenizer is None:
            from smartdoc.const import CONFIG
            tokenizer_model_name = CONFIG.get("GPT2_TOKENIZER_MODEL_NAME")
            tokenizer_model_path = CONFIG.get("GPT2_TOKENIZER_MODEL_PATH")
            if tokenizer_model_name is None or tokenizer_model_path is None:
                tokenizer_model_name = 'gpt2'
                tokenizer_model_path = '/opt/maxkb/model/tokenizer'
            
            TokenizerManage.tokenizer = GPT2TokenizerFast.from_pretrained(
                tokenizer_model_name,
                cache_dir=tokenizer_model_path,
                local_files_only=True,
                resume_download=False,
                force_download=False)
        return TokenizerManage.tokenizer
