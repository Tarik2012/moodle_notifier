from moodle_app.moodle_client import call

def calculate_course_progress(moodle_user_id, moodle_course_id):
    """
    Calcula el progreso real de un curso usando los SCORMs.
    """

    curso = call("core_course_get_contents", {
        "courseid": moodle_course_id
    })

    if isinstance(curso, dict) and curso.get("exception"):
        return 0.0

    # Buscar SCORMs
    scorm_ids = []
    for section in curso:
        for mod in section.get("modules", []):
            if mod["modname"] == "scorm":
                scorm_ids.append(mod["instance"])

    if not scorm_ids:
        return 0.0

    progreso_total = 0
    procesados = 0

    for scorm_id in scorm_ids:
        scoes = call("mod_scorm_get_scorm_scoes", {"scormid": scorm_id})
        sco_list = [
            s for s in scoes.get("scoes", [])
            if s.get("launch") and s.get("scormtype") == "sco"
        ]

        completados = 0
        total = len(sco_list)

        for sco in sco_list:
            track = call("mod_scorm_get_scorm_sco_tracks", {
                "userid": moodle_user_id,
                "scoid": sco["id"]
            })

            status = "notattempted"
            for t in track.get("data", {}).get("tracks", []):
                if t["element"] in ["cmi.core.lesson_status", "status"]:
                    status = t["value"]

            if status in ["completed", "passed"]:
                completados += 1

        progreso = (completados / total) * 100 if total else 0
        progreso_total += progreso
        procesados += 1

    return progreso_total / procesados if procesados else 0
