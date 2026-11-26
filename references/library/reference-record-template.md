# Reference record — шаблон DIS

- `id`: …
- `record_type`: trend_signal | reference_candidate | analysed_reference | calibration_benchmark | our_accepted_work | anti_example | studio_pattern
- `title / author / studio`: …
- `source_url / original_date / checked_on`: …
- `source_kind`: jury_award | curated | community_metrics | annual_trend_guide | live_product | studio_work | other
- `recognition`: факт, категория, год, цифры, URL-доказательство; если нет — unknown
- `observed_scope`: desktop/mobile/animation/interactions/screens; что **не** проверено
- `original_domain / original_function`: что источник реально решает; отличие от нашей задачи не является причиной отбраковки
- `observed_mechanism / observation_status`: увиденный принцип, реально проверенные экраны/состояния, что лишь предположение
- `alternative_target_function`: какую *новую*, потенциально даже неожиданную задачу принцип может решить у нас
- `transformation_plan / new_composition`: как переосмыслить механизм и художественно переработать в собственный язык
- `task_relevance`: high/medium/low/unknown **после** попытки аналогического переноса; не фильтр первичного поиска, указать причину
- `transferability`: high/medium/low/unknown + как адаптировать
- `external_recognition`: high/medium/low/unknown + тип сигнала (не сравнивать разнородные платформы как числовой рейтинг)
- `strong_mechanism`: конкретный визуальный/UX приём и почему работает
- `limitations / do_not_copy`: …
- `project_application / observed_result`: …
- `calibration_axes`: только проверенные оси + внешняя и внутренняя аргументация
- `DIS_score / human_feedback / gap`: если действительно были, иначе unknown
- `studio_signature_candidate`: optional + отдельно статус, никогда не автопромоут
- `status / last_review / checkpoint_commit`: …

**Promotion до calibration_benchmark:** недостаточно ссылки на награду/тренд/популярность; нужен независимый структурный разбор реальных артефактов, применимых осей, ограничений и источник внешнего подтверждения.


## События и выбор пользователя (Reference Engine v1)

- `source_id / event_id / run_id / project_id`: устойчивые идентификаторы, повтор event_id не удваивает запись.
- `evidence_status`: discovered | visually_inspected | analysed | applied | reviewed; повышение только по доказанному действию.
- `observation_evidence / inspected_at / inspected_state`: чем подтверждено; отсутствие evidence = not_checked.
- `mechanism_id / transformation_id / project_decision_id`: раздельные сущности источник → механизм → собственная переработка → решение.
- `chosen_option_ids[] / explicit_approval_scope`: фактический многовыбор арт-директора, без выдумывания причин.
- `persistence_status`: saved | manual_checkpoint_capture | persistence_failed | not_connected; не подменять сохранение в памяти беседы durable записью.
